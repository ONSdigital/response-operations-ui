class GulpError extends Error {
    constructor(message, fatal = true) {
        super()
        this.message = message
        this.fatal = fatal
    }
}

module.exports = {
    GulpError
}