/** @odoo-module **/

import { Component } from "@odoo/owl";

export class TablaResultBaloto extends Component {
    static template = "baloto.ResultsTable"

    static props = {
        results: { type: Object },
    }

}
