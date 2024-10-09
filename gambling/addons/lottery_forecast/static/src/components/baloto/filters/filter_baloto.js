/** @odoo-module **/

import { Component } from "@odoo/owl";

export class FilterBaloto extends Component {
    static template = "baloto.BalotoFilter"

    static props = {
        option: { type: String }
    }

}
