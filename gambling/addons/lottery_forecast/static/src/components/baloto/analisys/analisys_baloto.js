/** @odoo-module **/

import { Component } from "@odoo/owl";

export class AnalisysBaloto extends Component {
    static template = "baloto.BalotoAnalisys"

    static props = {
        option: { type: String },
        analisysBalotoPandas: {
            type: Function,
            optional: true,
        },
        gameOptions: {
            type: Object,
            optional: true,
        }
    }

    /**
     * Maneja el cambio en el análisis seleccionado
     * @param {Event} event - El evento de cambio
     */
    onChangeAnalysis(event) {
        const select = event.target
        const selectedOption = select.value
        const option = select.options[select.selectedIndex].dataset.option

        if (typeof this.props.analisysBalotoPandas === 'function') {
            this.props.analisysBalotoPandas(selectedOption, option)
        }
    }
}
