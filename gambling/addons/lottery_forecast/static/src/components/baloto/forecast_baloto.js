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
            loading: false,
            error: null,
            selectedAnalysis: "",
            option: "",
        })
        this.gameOptions = this.getGameOptions()
    }

    getGameOptions() {
        return [
            {
                name: 'Baloto',
                options: this.getOptionsForGame('Baloto')
            },
            {
                name: 'Revancha',
                options: this.getOptionsForGame('Revancha')
            },
            {
                name: 'MiLoto',
                options: this.getOptionsForGame('MiLoto', false)
            }
        ]
    }

    getOptionsForGame(gameName, includeFrequency116 = true) {
        const options = [
            { value: `frequency-${gameName}`, label: 'Appearances by number' },
            { value: `pair-${gameName}`, label: `Pair more frequency, ${gameName}` },
            { value: `three-${gameName}`, label: `Three numbers more frequency, ${gameName}` },
            { value: `four-${gameName}`, label: `Four numbers more frequency, ${gameName}` },
            { value: `five-${gameName}`, label: `Five numbers more frequency, ${gameName}` },
        ]
        if (includeFrequency116) {
            options.splice(1, 0, { value: `116-frequency`, label: 'Appearances by number, 1-16' })
        }
        return options
    }

    openHistoricalView(lotteryType = "") {
        const context = lotteryType
            ? { [`search_default_lottery_type_id_${lotteryType}`]: 1, search_default_group_by_winner: 1 }
            : {};  // Si lotteryType está vacío, no aplica filtros

        this.env.services.action.doAction({
            name: `Historical ${lotteryType || "All"}`,
            type: "ir.actions.act_window",
            res_model: "lottery.baloto",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
                [false, "graph"],
            ],
            context: context,
        });
    }

    async analisysBalotoPandas(analysisType = null, option = null) {
        if (!analysisType || !option) {
            this.showNotification("Select an option!", "Error", "danger")
            this.resetState()
            return
        }

        this.state.loading = true
        this.state.error = null

        const method = this.getMethodForAnalysis(analysisType)

        if (!method) {
            this.showNotification("Invalid analysis type!", "Error", "danger")
            this.resetState()
            return
        }

        try {
            const data = this.prepareDataForAnalysis(analysisType, option)
            this.state.results = await this.env.services.orm.call('lottery.baloto', method, data)
            this.state.option = option
            this.showNotification("Success!!!", "Amazing Creations", "success")
        } catch (error) {
            console.error('Error fetching data:', error)
            this.state.error = error.message || "An error occurred"
            this.showNotification("Failed to fetch data!", "Error", "danger")
        } finally {
            this.state.loading = false
            this.render()
        }
    }

    getMethodForAnalysis(analysisType) {
        const methodMap = {
            'frequency': 'analyze_frequencies_pandas',
            'pair': 'analyze_frequency_numbers_pandas',
            'three': 'analyze_frequency_numbers_pandas',
            'four': 'analyze_frequency_numbers_pandas',
            'five': 'analyze_frequency_numbers_pandas',
        }
        const type = analysisType.split('-')[0]
        return type.endsWith('116') ? 'frequency_1_16_pandas' : methodMap[type]
    }

    prepareDataForAnalysis(analysisType, option) {
        const data = [option]
        const type = analysisType.split('-')[0]
        if (['three', 'four', 'five'].includes(type)) {
            data.push(parseInt(type === 'three' ? 3 : type === 'four' ? 4 : 5))
        }
        return data
    }

    showNotification(message, title, type) {
        this.env.services.notification.add(message, {
            title: title,
            type: type,
        })
    }

    resetState() {
        this.state.results = []
        this.state.option = ""
        this.state.loading = false
        this.state.error = null
    }
}

registry.category("actions").add("action.BalotoForecast", BalotoForecast)
