const express = require('express');
const fs = require( 'fs' );
const xmlCrypto = require( 'xml-crypto' );
const jsdom = require( 'jsdom' );
const DOMParser = new (new jsdom.JSDOM( '' )).window.DOMParser;
const zlib = require( 'zlib' );

const PORT = 1337;
const app = express();

const IDPHOST = process.env.IDPHOST || 'http://localhost:9000';
const IDPURL = IDPHOST + '/application/saml/flaggetter/sso/binding/init/'

function doLogin( res ) {
	res.redirect( IDPURL );
}


function verifySaml( xmlString, xmlDoc ) {
	const sig = new xmlCrypto.SignedXml();
	try {
		sig.publicCert = fs.readFileSync( 'public.pem', 'latin1' );
	} catch ( e ) {
		throw new Error( "Missing certificate." );
	}
	if ( !sig.publicCert ) {
		throw new Error( "Missing cert" );
	}

	const rootId = xmlDoc.documentElement.getAttribute( 'ID' );
	if ( !rootId || rootId.includes( '"' ) || rootId.includes( "\\" ) ) {
		throw new Error( 'invalid id' );
	}
	const signedInfoElm = xmlDoc.querySelectorAll( ':root > Signature' );
	if ( signedInfoElm.length !== 1 ) {
		throw new Error( 'wrong number sigs' );
	}
	if ( signedInfoElm[0].querySelectorAll( 'Reference[URI="#' + rootId + '"]' ).length !== 1 ) {
		throw new Error( 'invalid id' );
	}
	if ( signedInfoElm[0].querySelectorAll( 'Transform' ).length > 2 ) {
		throw new Error( "too many transforms" );
	}

	sig.loadSignature( signedInfoElm[0].outerHTML );
	sig.checkSignature( xmlString );
	if ( sig.getSignedReferences().length !== 1 ) {
		throw new Error( 'Signature mismatch' );
	}
}

app.get( '/flag', ( req, res ) => {
	if ( req.query.SAMLResponse ) {
		const xmlString = zlib.inflateRawSync( Buffer.from( req.query.SAMLResponse, 'base64' ) ).toString();
		const xmlDoc = DOMParser.parseFromString( xmlString, 'application/xml' );
		if ( !xmlDoc || !xmlString || xmlDoc.documentElement.tagName === 'parsererror' ) {
			throw new Error( "invalid saml xml" );
		}
		console.log( "Recieved the following SAML:\n" + xmlString );
		verifySaml( xmlString, xmlDoc );
		const username = xmlDoc.querySelector(
			'Attribute[Name="http://schemas.goauthentik.io/2021/02/saml/username"] AttributeValue'
		)?.textContent;
		if ( username === 'akadmin' ) {
			res.type( 'text/plain' ).send( process.env.FLAG || 'flag{fake}' );
		} else {
			res.type( 'text/plain' ).status(401).send( `Hello ${username}. You are not authorized to view the flag.` );
		}
	} else {
		doLogin(res);
	}
} );

app.get( '/', ( req, res ) => {
	res.send( '<a style="font-size:5em" href="/flag">View flag?</a>' );
} );

app.listen( PORT, () => {
	console.log( "Running on PORT " + PORT );
});
