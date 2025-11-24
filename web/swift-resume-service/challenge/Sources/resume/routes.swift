import Vapor
import SwiftSoup

struct Foo: Content {
	var first: String
	var second: String
}

// I don't know what i am doing. FIXME is this fine?
nonisolated(unsafe) var resumes: [String: String] = [:]
nonisolated(unsafe) var templates: [String: Int] = [:]

struct NewResume: Content {
	var template: String
	var name: String
	var email: String
	var currentPosition: String
	var currentPositionDesc: String
}

func esc(_ input: String ) -> String {
	var text = input
	text = text.replacingOccurrences( of: "<", with: "&lt;" )
	text = text.replacingOccurrences( of: ">", with: "&gt;" )
	text = text.replacingOccurrences( of: "\"", with: "&quot;" )
	text = text.replacingOccurrences( of: "'", with: "&apos;" )
	return text
}

func validateTemplate(_ input: String) throws -> String {
	let allowed = try Whitelist.relaxed()
	try allowed.addTags( "link" )
	try allowed.addAttributes( "link", "rel", "href" )
	return try SwiftSoup.clean(input, allowed) ?? "Sanitizer failed"
}

func routes(_ app: Application) throws {
	app.get { req async throws in
		try await req.view.render( "index" )
	}

	app.post("resumes") { req throws in
		let input = try req.content.decode(NewResume.self)
		let uuid = UUID().uuidString
		var finalText = input.template
		let count = templates[finalText] ?? 1
		if count == 1 {
			// First time seeing this template. Make sure it is
			// safe and create a metadata entry for it.
			finalText = try validateTemplate( finalText )
		}
		// Update the use count.
		templates[finalText] = count + 1 
		finalText = finalText.replacingOccurrences( of: "$email", with: esc(input.email) )
		finalText = finalText.replacingOccurrences( of: "$name", with: esc(input.name) )
		finalText = finalText.replacingOccurrences( of: "$currentPositionDesc", with: esc(input.currentPositionDesc) )
		finalText = finalText.replacingOccurrences( of: "$currentPosition", with: esc( input.currentPosition) )
		resumes[uuid] = finalText
		return req.view.render( "created", [ "resumeId": uuid, "count": String(count) ] )
	}

	app.get("resumes", ":uuid") { req throws in
		let uuid = req.parameters.get( "uuid" )!
		if let resume = resumes[uuid] {
			let b = Response.Body(stringLiteral: resume)
			return Response(status: .ok, headers: ["Content-Type": "text/html; charset=UTF-8"], body: b )
		} else {
			throw Abort(.notFound)
		}
	}
}
