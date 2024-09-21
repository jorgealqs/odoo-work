/** @odoo-module **/

import { registry } from '@web/core/registry';
import { Layout } from '@web/search/layout';
import { getDefaultConfig } from '@web/views/view';
import { Component, useSubEnv, useState } from '@odoo/owl';
import { useService } from "@web/core/utils/hooks";

export class ApiFootballConfigOwl extends Component {
    static template = "config.apiFootball";
    static components = { Layout };

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            }
        });

        this.state = useState({
            matches: [],
            loading: true,
            error: null,
            resultHome: [], // Estado para el standing del equipo local
            resultAway: []  // Estado para el standing del equipo visitante
        });

        this.orm = useService("orm");

        if (!this.orm) {
            this.state.error = 'ORM service is not available.';
            this.state.loading = false;
            return;
        }

        this.loadMatches();

        this.events = {
            'click .card': this.handleCardClick.bind(this)
        };
    }

    async loadMatches() {
        try {
            const today = new Date().toISOString().split('T')[0];
            const startOfDay = `${today} 00:00:00`;
            const endOfDay = `${today} 23:59:59`;

            const result = await this.orm.searchRead(
                'football.fixture',
                [
                    ['date', '>=', startOfDay],
                    ['date', '<=', endOfDay]
                ],
                [],
                {
                    order: 'country_id, league_id, date'
                }
            );

            this.state.matches = result;
            this.state.loading = false;
        } catch (error) {
            this.state.error = error.message || 'An error occurred while fetching matches.';
            this.state.loading = false;
        }
    }

    async handleCardClick(event) {
        try {
            const { fixtureId, homeId, awayId, roundId, leagueId } = event.currentTarget.dataset;
            const homeIdValue = homeId.split(',')[0];
            const awayIdValue = awayId.split(',')[0];
            const roundIdValue = roundId.split(',')[0];
            const leagueIdValue = leagueId.split(',')[0];

            const [resultHome, resultAway] = await Promise.all([
                this.fetchTeamStanding(homeIdValue, leagueIdValue),
                this.fetchTeamStanding(awayIdValue, leagueIdValue)
            ]);

            // Almacenar los resultados en el estado
            this.state.resultHome = resultHome;
            this.state.resultAway = resultAway;

            console.log({ fixtureId, resultHome, resultAway });
        } catch (error) {
            console.error('Error fetching team standings:', error);
        }
    }

    async fetchTeamStanding(teamId, leagueIdValue) {
        try {
            return await this.orm.searchRead(
                'football.standing',
                [
                    ["league_id.id", "=", leagueIdValue],
                    ["team_id.id", "=", teamId]
                ],
                []
            );
        } catch (error) {
            console.error('Error fetching team standing:', error);
            return [];
        }
    }
}

// Registrar el componente en la categoría de acciones
registry.category("actions").add("config.testAction", ApiFootballConfigOwl);