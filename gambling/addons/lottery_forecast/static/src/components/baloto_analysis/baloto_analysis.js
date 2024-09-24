/** @odoo-module **/

import { registry } from '@web/core/registry'
import { Layout } from '@web/search/layout'
import { getDefaultConfig } from '@web/views/view'
import { Component, useSubEnv, useState } from '@odoo/owl'
import { useService } from "@web/core/utils/hooks"


export class LotteryBalotoAnalysis extends Component {
    static template = "analysis.LotteryBaloto"
    static components = { Layout }

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            }
        })
        this.state = useState({
            results: [],
            loading: true,
            error: null,
            selectedAnalysis: "",
            option: "",
        })
        this.orm = useService("orm")
        this.notificationService = useService("notification")
    }

    changeAnalysis(event) {
        const option = event.target.selectedOptions[0].getAttribute('data-option')
        this.state.selectedAnalysis = event.target.value
        this.analysis(this.state.selectedAnalysis, option)
    }

    async analysis(analysisType=Null, option=Null) {

        switch (
            analysisType
        ) {
            case 'frequency-MiLoto':
            case 'frequency-Revancha':
            case 'frequency-Baloto':
                try {
                    // Llamada al método del backend enviando el option (tipo de lotería) como parámetro
                    const frequencyData = await this.orm.call('lottery.baloto', 'analyze_frequencies_pandas', [option])

                    // Procesar los datos recibidos del backend
                    this.state.results = frequencyData
                    this.state.option = option
                    this.render() // Renderizar los resultados actualizados
                    this.notificationService.add("Gook Luck, God is with you!!!", {
                        title: "Amazing Creations",
                        type: "success",
                    })
                } catch (error) {
                    console.error('Error fetching frequency data:', error)
                }
                break

            default:
                this.notificationService.add("Select an option!", {
                    title: "Error",
                    type: "danger",
                })
                this.state.results = []
                this.state.option = ""
                break
        }

    }

    // Método para filtrar por día
    filterByDay(event) {
        // Verifica si el evento y el target existen
        if (event && event.target) {
            const day = event.target.getAttribute('data-day')

            if (day) {
                // Selecciona los elementos con la clase adecuada
                const listItems = document.querySelectorAll(`li.day-${day}`)

                // Esconder todos los elementos y mostrar solo los del día seleccionado
                document.querySelectorAll('li').forEach(li => li.style.display = 'none')
                listItems.forEach(item => item.style.display = 'block')
            } else {
                console.error('No se encontró el atributo data-day en el elemento.')
            }
        } else {
            console.error('El evento no contiene un target válido.')
        }
    }

    // Limpiar el filtro
    clearFilter() {
        // Mostrar todos los elementos
        document.querySelectorAll('li').forEach(li => li.style.display = 'block')
    }

}

registry.category("actions").add("action.LotteryBalotoAnalysis", LotteryBalotoAnalysis)