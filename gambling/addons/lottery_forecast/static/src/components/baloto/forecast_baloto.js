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

    async analisysBalotoPandas(analysisType = null, option = null) {
        const successNotification = () => {
            this.env.services.notification.add("Success!!!", {
                title: "Amazing Creations",
                type: "success",
            });
        };

        const errorNotification = (error) => {
            console.error('Error fetching data:', error);
            this.env.services.notification.add("Failed to fetch data!", {
                title: "Error",
                type: "danger",
            });
        };

        const callBackendMethod = async (model, method) => {
            try {
                this.state.results = await this.env.services.orm.call(model, method, [option]);
                this.state.option = option;
                this.render(); // Renderizar los resultados actualizados
                successNotification();
            } catch (error) {
                errorNotification(error);
            }
        };

        switch (analysisType) {
            case 'frequency-MiLoto':
            case 'frequency-Revancha':
            case 'frequency-Baloto':
                await callBackendMethod('lottery.baloto', 'analyze_frequencies_pandas');
                break;

            case 'frequency-Baloto116':
            case 'frequency-Revancha116':
                await callBackendMethod('lottery.baloto', 'frequency_1_16_pandas');
                break;

            default:
                this.env.services.notification.add("Select an option!", {
                    title: "Error",
                    type: "danger",
                });
                this.state.results = [];
                this.state.option = "";
                break;
        }
    }
}

registry.category("actions").add("action.BalotoForecast", BalotoForecast)