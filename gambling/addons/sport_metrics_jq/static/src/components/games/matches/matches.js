/** @odoo-module */

import { Component, useRef } from "@odoo/owl"

export class MatchesItem extends Component {
    static template = "games.MatchesItem"
    static props = {
        data: {
            type: Object,
        },
        onClickFetchFixture:{
            type: Function,
            optional: true
        }
    }

    setup(){
        this.homeTeamSpan = useRef("homeTeamSpan")
        this.awayTeamSpan = useRef("awayTeamSpan")
    }

    onClickFetchFixture(event){
        if (this.props.onClickFetchFixture) {
            const data = {
                homeTeamSpan: this.homeTeamSpan.el.innerText,
                awayTeamSpan: this.awayTeamSpan.el.innerText,
                idTable: this.props.data.id
            }
            this.props.onClickFetchFixture(data)
        }
    }
}