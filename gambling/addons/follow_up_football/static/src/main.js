/** @odoo-module **/

import { browser } from "@web/core/browser/browser"
import { whenReady } from "@odoo/owl"
import { mountComponent } from "@web/env"
import { ApiFootball } from "./api_football"
import { ApiFootballManual } from "./manual_football/manual"

whenReady(() => {
    const path = window.location.pathname

    if (path === '/games') {
        // Mount the ApiFootball component for the '/games' route
        mountComponent(ApiFootball, document.body, { dev: true, name: "Api Football" })
    } else if (path === '/manual-football') {
        // Mount the ApiFootballManual component for the '/manual-football' route
        mountComponent(ApiFootballManual, document.body, { dev: true, name: "Api Football Manual" })
    }
})



/**
 * This code is iterating over the cause property of an error object to console.error a string
 * containing the stack trace of the error and any errors that caused it.
 * @param {Event} ev
 */
function logError(ev) {
    ev.preventDefault()
    let error = ev ?.error || ev.reason

    if (error.seen) {
        // If an error causes the mount to crash, Owl will reject the mount promise and throw the
        // error. Therefore, this if statement prevents the same error from appearing twice.
        return
    }
    error.seen = true

    let errorMessage = error.stack
    while (error.cause) {
        errorMessage += "\nCaused by: "
        errorMessage += error.cause.stack
        error = error.cause
    }
    console.error(errorMessage)
}

browser.addEventListener("error", (ev) => {logError(ev)})
browser.addEventListener("unhandledrejection", (ev) => {logError(ev)})
