/** @odoo-module **/

import { registry } from '@web/core/registry'
import { Layout } from '@web/search/layout'
import { Component, useState, useRef } from '@odoo/owl'
import { MatchesItem } from "./matches/matches"
import { MatchesFilter } from "./filters/filters_matches"


class GamesFootball extends Component {
    static template = "games.FootballMatches"
    static components = { Layout, MatchesItem, MatchesFilter }

    setup() {
        this.loadMatches()
        this.modalRef = useRef("modalRef")
        this.display = {
            controlPanel: {},
        }
        this.state = useState({
            games: [],
            prediction: [],
            fixtures: [],
            loading: true,
            error: null,
            teamsVs : "Match Details",
            currentDisplay: "default", // <- Controla qué display mostrar
        })
    }

    // Funciones para cambiar el display
    showDefaultDisplay() {
        this.state.currentDisplay = "default";
    }

    showInfoDisplay() {
        this.state.currentDisplay = "info";
    }

    async fetchFixture(data=null) {
        try {
            const matches = await this.env.services.rpc("/match/details", {fixture_id_table:data.idTable})
            const modalRef = this.modalRef.el
            $(modalRef).modal('show')
            let homeTeamName = data.homeTeamSpan
            let awayTeamName = data.awayTeamSpan
            this.state.teamsVs = `${homeTeamName} vs ${awayTeamName}`
            this.state.prediction = matches.fixture[0]
        } catch (error) {
            this.state.prediction = []
            console.error('Error fetching matches:', error)
        }
    }

    async loadMatches(date = false) {
        try {
            let startOfDay, endOfDay
            if (date){
                startOfDay = `${date} 00:00:00`
                endOfDay = `${date} 23:59:59`
            }else{
                const nowInBogota = new Date().toLocaleString('en-CA', { timeZone: 'America/Bogota', hour12: false })
                const [date, time] = nowInBogota.split(', ')
                startOfDay = `${date} ${time}`
                endOfDay = `${date} 23:59:59`
            }
            const data = {
                'startOfDay':startOfDay,
                'endOfDay':endOfDay
            }
            const result = await this.env.services.rpc("/match/all", data)
            this.state.games = result.fixtures
            this.state.loading = false
        } catch (error) {
            this.state.error = error.message || 'An error occurred while fetching matches.'
            this.state.loading = false
            console.log("Error: ",this.state.error)
        }
    }

    openLeaguesView(){
        this.env.services.action.doAction({
            name: "Leagues",
            type: "ir.actions.act_window",
            res_model: "sport.metrics.jq.league",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            // domain: [['follow', '=', 1]],
            context: {
                search_default_group_continent: 1,
                search_default_group_country: 1,
                search_default_group_follow: 1,
            }
        })
    }

    filterMatchesByDate(selectedDate){
        this.loadMatches(selectedDate)
    }

    openCountries() {
        this.env.services.action.doAction({
            name: "Countries",
            type: "ir.actions.act_window",
            res_model: "sport.metrics.jq.country",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            context: {
                search_default_group_continent: 1,
                search_default_group_session: 1,
            }
        })
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async syncFixtures() {
        const games = this.state.games;
        let requestCount = 0;

        for (const game of games) {
            const data = {
                fixture_id_table: game.id,
                fixture_id: game.fixture_id,
                league_id: game.id_league,
                session_id: game.session_id,
            };

            try {
                await this.env.services.rpc("/sport/metrics/sync_predictions", {
                    params: data,
                });
            } catch (error) {
                console.error("Error:", error);
            }

            requestCount++;
            if (requestCount % 10 === 0) {
                console.log("Esperando 1 minuto para evitar exceder el límite de peticiones...");
                await this.sleep(60 * 1000); // Esperar 60 segundos después de 10 peticiones
            } else {
                await this.sleep(500); // Esperar 500 ms entre cada petición
            }
        }
    }

    async showInfo() {
        const result = await this.env.services.rpc("/sport/metrics/info", {});
        // console.log("Result:", result);
        this.state.fixtures = result.fixtures;
        this.state.currentDisplay = "info";
    }

}

registry.category("actions").add("metrics.GamesFootball", GamesFootball)