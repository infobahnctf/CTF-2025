<?php

if ( isset( $_REQUEST['xml'] ) ) {
	header( 'Content-Type: application/xml; charset=UTF-8' );

	$x = xml_parser_create_ns( 'utf-8' );
	xml_set_default_handler( $x, function( $p, $data ) { echo $data; } );
	xml_set_character_data_handler( $x, function( $parser, $data ) {
		echo htmlspecialchars(
			str_replace(
				['E', 'K', 'C', 'A', 'S', 'I', 'M'],
				[ '3', '>-', '<', '4', '5', '1', '/V\\' ],
				strtoupper( $data )
    			)
  		);
 	});
	xml_set_start_namespace_decl_handler( $x, function( $parser, $prefix, $uri ) {
		die( "<!-- No namespaces allowed. Exiting -->" );
	} );
	xml_set_processing_instruction_handler( $x, function( $parser, $target, $data ) {
		if ( $target === 'xml-stylesheet' ) {
			echo "<!-- XML is already pretty enough -->";
		} else {
			echo "<?$target $data?>";
		}
	} );

	if ( !xml_parse( $x, $_REQUEST['xml'], true ) ) {
		@header( 'HTTP/1.1 500 error' );
		@header( 'Error: ' . xml_error_string( xml_get_error_code( $x ) ) );
		echo '<!-- Error: ' . xml_error_string( xml_get_error_code( $x ) ) . ' -->';
	}

} else {
?>
<!doctype html>
<html>
<head>
<title>1337 XML converter</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<h1>XML 1337 Converter</h1>
<p>
Wish your XML files were cooler? Wait no more with our all new 1337 converter for XML files. We'll leave the structural elements of the file alone and just convert the text content.
</p>
<label>XML:</label><br>
<form action="/" method="POST">
<textarea name="xml" id="xml" cols="80" rows="15" placeholder="<&#x3f;xml version=&quot;1.0&quot;&#x3f;>" required>
</textarea>
<br>
<input type="submit" value="1337-ify">
</form>
<br><a href="https://xml-translator-bot-web.challs2.infobahnc.tf">Admin bot</a>
</body>
</html>
<?php

}
