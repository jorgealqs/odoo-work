/** @odoo-module **/

import { Component } from "@odoo/owl";

export class HistoricalButton extends Component {
    static template = "baloto.HistoricalButton";

    static props = {
        option: { type: String },
        label: { type: String },
        size: { type: Number, default:1, optional: true },
        openHistoricalView: { type: Function, optional: true }
    }

    onClickButton(){
        if (this.props.openHistoricalView) {
            this.props.openHistoricalView(this.props.option)
        }
    }

}
