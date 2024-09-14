/** @odoo-module **/

import { Component, useState } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"

export class ApiFootball extends Component {
    static template = "follow_up_football.games"
    static props = {}

    setup() {
        this.state = useState({
            matches: [], // Aquí se almacenarán los resultados
            loading: true, // Indica si los datos están cargando
            error: null // Aquí se almacenará cualquier error
        })

        this.orm = useService("orm") // Obtén el servicio orm

        if (!this.orm) {
            console.error("ORM service is not available.")
            this.state.error = 'ORM service is not available.'
            this.state.loading = false
            return
        }
        this.loadMatches()
    }

    async loadMatches() {
        try {
            // Define la fecha de hoy en formato YYYY-MM-DD
            const today = new Date().toISOString().split('T')[0]

            // Define el inicio y fin del día
            const startOfDay = `'${today} 00:00:00'`
            const endOfDay = `'${today} 23:59:59'`

            // Llama al método del modelo 'football.fixture' usando orm
            const result = await this.orm.searchRead(
                'football.fixture',
                [
                    ['date','>=',startOfDay],
                    ['date','<=',endOfDay]
                ],
                [], // Campos a obtener
                // Fields to retrieve (e.g. ['date', 'home_team_id', 'away_team_id', 'league_id'])
                {
                    order: 'league_id DESC'
                }
            )
            console.log(result)
            // Agrega esta línea para verificar el resultado
            // Actualiza el estado con los resultados
            this.state.matches = result
            this.state.loading = false
        } catch (error) {
            // Manejo de errores
            console.error("Error in loadMatches:", error)
            this.state.error = error.message || 'An error occurred while fetching matches.'
            this.state.loading = false
        }
    }
}