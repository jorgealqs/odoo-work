/** @odoo-module **/

import { registry } from '@web/core/registry'
import { Layout } from '@web/search/layout'
import { Component, useState } from '@odoo/owl'
import { useService } from "@web/core/utils/hooks"
import { MatchViewItem } from "./match_item/match_item_view"


class MatchAction extends Component {
    static template = "metrics.MatchView"
    static components = { Layout, MatchViewItem }

    setup() {

        this.display = {
            controlPanel: {},
        }

        this.state = useState({
            matches: [],
            loading: true,
            error: null,
            resultHome: [],
            resultAway: [],
            selectedMatch: [],
            teams_vs: 'Match Details',
        })

        this.orm = useService("orm")
        this.action = useService("action")
        this.rpc = useService("rpc")
        // Log to see if rpc is correctly loaded

        this.loadMatches()

        // Formatear la fecha
        this.formatDate = (date) => {
            const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
            return new Date(date).toLocaleDateString('en-US', options);
        }
    }

    async loadMatches(date = false) {
        try {
            let startOfDay, endOfDay;
            if (date){
                startOfDay = `${date} 00:00:00`;
                endOfDay = `${date} 23:59:59`;
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
            const result = await this.rpc("/match/all", data)
            console.log(result)
            this.state.matches = result.fixtures
            this.state.loading = false
        } catch (error) {
            this.state.error = error.message || 'An error occurred while fetching matches.'
            this.state.loading = false
            console.log("Error: ",this.state.error)
        }
    }

    openCustomerView() {
        this.action.doAction("base.action_partner_form")
    }

    openLeaguesView() {
        this.action.doAction({
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
            }

        })
    }

    async fetchMatchDetails(fixture_id_table, fixture_id) {
        try {
            const matches = await this.rpc("/match/details", {fixture_id_table:fixture_id_table})
            this.state.teams_vs = $(`.vs-${fixture_id}`).text()
            // Procesar los detalles de los partidos
            console.log(matches.fixture[0], fixture_id);
            this.state.selectedMatch = matches.fixture[0]
            $('#matchDetailsModal').modal('show')
        } catch (error) {
            console.error('Error fetching matches:', error);
        }
    }

    filterMatchesByDate(){
        let selectedDate = document.getElementById('match_date').value
        this.loadMatches(selectedDate)
    }
}

registry.category("actions").add("metrics.Match", MatchAction)