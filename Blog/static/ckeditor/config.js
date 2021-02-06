/**
 * @license Copyright (c) 2003-2020, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
    config.extraPlugins = 'markdown';
    // config.allowedContent= true;
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	config.uiColor = '#AADC6E';
	config.enterMode = 3; // pressing the ENTER KEY input <br/>
	// // config.shiftEnterMode = CKEDITOR.ENTER_P; //pressing the SHIFT + ENTER KEYS input <p>
	// config.autoParagraph = true; // stops automatic insertion of <p> on focus
	// config.ignoreEmptyParagraph = false;
	// config.fillEmptyBlocks = false; // Prevent filler nodes in all empty blocks.
};
