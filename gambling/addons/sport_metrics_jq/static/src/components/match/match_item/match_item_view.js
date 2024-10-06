/** @odoo-module */

import { Component } from "@odoo/owl"

export class MatchViewItem extends Component {
    static template = "metrics.MatchViewItem"
    static props = {
        slots: {
            type: Object,
            shape: {
                default: Object
            },
        },
        size: {
            type: Number,
            default: 1,
            optional: true,
        },
    }
}