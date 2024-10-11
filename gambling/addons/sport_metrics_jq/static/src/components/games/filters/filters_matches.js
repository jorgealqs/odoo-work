/** @odoo-module */

import { Component, useRef } from "@odoo/owl"

export class MatchesFilter extends Component {
    static template = "games.MatchesFilter"
    static props = {
        onClickShowMatches:{
            type: Function,
            optional: true
        }
    }

    setup() {
        // Crear una referencia para el input
        this.matchDateRef = useRef("matchDate")
    }

    onClickShowMatches(event) {
        const matchDateEl = this.matchDateRef.el
        if (matchDateEl) {
            const matchDate = matchDateEl.value
            if (this.props.onClickShowMatches) {
                this.props.onClickShowMatches(matchDate)
            }
        } else {
            console.error("Error: No se pudo acceder a la referencia matchDate")
        }
    }
}