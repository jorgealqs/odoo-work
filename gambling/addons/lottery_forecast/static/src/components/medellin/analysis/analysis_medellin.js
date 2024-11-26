/** @odoo-module **/

import { Component } from "@odoo/owl";

export class AnalisysLotteryMedellin extends Component {
    static template = "lottery.LotteryMedellinAnalysis"

    static props = {
        option: { type: String },
        getAnalysisMedellin: {
            type: Object,
            optional: true,
        },
        analysisMedellinPandas: {
            type: Function,
            optional: true,
        },
    }

    /**
     * Maneja el cambio en el análisis seleccionado
     * @param {Event} event - El evento de cambio
     */
    onChangeAnalysis(event) {
        const select = event.target
        const selectedOption = select.value
        const option = select.options[select.selectedIndex].dataset.option

        if (typeof this.props.analysisMedellinPandas === 'function') {
            this.props.analysisMedellinPandas(selectedOption, option)
        }
    }
}
