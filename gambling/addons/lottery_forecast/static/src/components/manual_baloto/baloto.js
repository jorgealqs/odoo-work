/** @odoo-module **/

import { registry } from '@web/core/registry'
import { Layout } from '@web/search/layout'
import { getDefaultConfig } from '@web/views/view'
import { Component, useSubEnv } from '@odoo/owl'

export class LotteryBalotoManual extends Component {
    static template = "manual.LotteryBaloto"
    static components = { Layout }

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            }
        })
    }
}

registry.category("actions").add("action.LotteryBalotoManual", LotteryBalotoManual)