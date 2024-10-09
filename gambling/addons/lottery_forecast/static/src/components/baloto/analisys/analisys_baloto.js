/** @odoo-module **/

import { Component } from "@odoo/owl";

export class AnalisysBaloto extends Component {
    static template = "baloto.BalotoAnalisys"

    static props = {
        option: { type: String },
        analisysBalotoPandas:{
            type: Function,
            optional: true
        }
    }

    onChangeAnslisys(event){
        const selectedOption = event.target.value
        const option = event.target.options[event.target.selectedIndex].dataset.option
        if (this.props.analisysBalotoPandas) {
            this.props.analisysBalotoPandas(selectedOption, option)
        }
    }

}
