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
            loading: true,
            error: null,
            teamsVs : "Match Details"
        })
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
            domain: [['follow', '=', 1]],
            context: {
                search_default_group_continent: 1,
                search_default_group_country: 1,
            }
        })
    }

    filterMatchesByDate(selectedDate){
        this.loadMatches(selectedDate)
    }

}

registry.category("actions").add("metrics.GamesFootball", GamesFootball)