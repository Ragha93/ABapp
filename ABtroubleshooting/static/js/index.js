const cathodeVersions = require('cathode-versions-javascript');

const cathodeConfig = {
    siteName: "Kraghaprojects",
    appName: "Automationtools",                       // optional
    realm: "USAmazon",                                    // optional
    httpRequestId: "00000000-0000-0000-0000-000000000000" // optional
}

const scriptTags = cathodeVersions.getSpectrometerScriptTags(cathodeConfig, configUtils.isProdBuild);

// Adding to an HTML Webpack Plugin
const plugin = new HtmlWebpackPlugin({
    ...
    siteName: cathodeConfig.siteName,
    appName: cathodeConfig.appName,
    boomerangLoaderScript: scriptTags.boomerangLoaderScript,
    cathodeListenerScripts: scriptTags.listenerScripts,
    cathodeLoaderScript: scriptTags.cathodeScript
}),
