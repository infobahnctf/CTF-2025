module app;

import std.process;
import vibe.core.core;
import vibe.http.proxy;
import vibe.http.router;
import vibe.http.server;
import vibe.http.auth.basic_auth;
import vibe.http.status;
import std.functional : toDelegate;

bool checkpw(string username, string password) {
    return username == "logo" && password == environment.get("BASIC_PASSWORD", "tmp_pass");
}

int main(string[] args)
{
    auto settings = new HTTPServerSettings;
    settings.port = 8080;
    settings.bindAddresses = ["0.0.0.0"];

    auto router = new URLRouter;
    auto proxyHandler = reverseProxyRequest(environment.get("BACKEND_ORIGIN", "0.0.0.0"), 9999); 

    router.any("*", performBasicAuth("Logo", toDelegate(&checkpw)));
    router.get("*", (HTTPServerRequest req, HTTPServerResponse res) {
		return proxyHandler(req, res);
	});
    
    listenHTTP(settings, router);
    return runApplication(&args);
}