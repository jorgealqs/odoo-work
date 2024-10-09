/** @odoo-module **/

import { Component, useState } from "@odoo/owl"
import { registry } from "@web/core/registry"
import { Layout } from "@web/search/layout"
import { HistoricalButton } from "./button_historical/button"
import { AnalisysBaloto } from "./analisys/analisys_baloto"
import { TablaResultBaloto } from "./tabla_result/tabla_result"


export class BalotoForecast extends Component {
    static template = "baloto.BalotoForecast"
    static components = { Layout, HistoricalButton, AnalisysBaloto, TablaResultBaloto }

    setup() {
        this.display = {
            controlPanel: {
                "top-right": false,
                "bottom-right": false,
            },
        }
        this.state = useState({
            results: [],
            loading: true,
            error: null,
            selectedAnalysis: "",
            option: "",
        })
    }

    openHistoricalView(lotteryType = "") {
        const context = {}
        if (lotteryType) {
            context[`search_default_lottery_type_id_${lotteryType}`] = 1
        }

        this.env.services.action.doAction({
            name: `Historical ${lotteryType}`,
            type: "ir.actions.act_window",
            res_model: "lottery.baloto",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
            ],
            context: context,
        })
    }

    async analisysBalotoPandas(analysisType=null, option=null){
        switch (
            analysisType
        ) {
            case 'frequency-MiLoto':
            case 'frequency-Revancha':
            case 'frequency-Baloto':
                try {
                    // Llamada al método del backend enviando el option (tipo de lotería) como parámetro
                    this.state.results = await this.env.services.orm.call('lottery.baloto', 'analyze_frequencies_pandas', [option])
                    // Procesar los datos recibidos del backend
                    this.state.option = option
                    console.log(this.state.results)
                    this.render() // Renderizar los resultados actualizados
                    this.env.services.notification.add("Success!!!", {
                        title: "Amazing Creations",
                        type: "success",
                    })
                } catch (error) {
                    console.error('Error fetching frequency data:', error)
                }
                break

            default:
                this.env.services.notification.add("Select an option!", {
                    title: "Error",
                    type: "danger",
                })
                this.state.results = []
                this.state.option = ""
                break
        }
    }
}

registry.category("actions").add("action.BalotoForecast", BalotoForecast)