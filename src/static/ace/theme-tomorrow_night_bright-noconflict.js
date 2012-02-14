ace.define("ace/theme/tomorrow_night_bright", ["require", "exports", "module"], function (a, b, c) {
    b.isDark = !0, b.cssClass = "ace-tomorrow-night-bright", b.cssText = ".ace-tomorrow-night-bright .ace_editor {  border: 2px solid rgb(159, 159, 159);}.ace-tomorrow-night-bright .ace_editor.ace_focus {  border: 2px solid #327fbd;}.ace-tomorrow-night-bright .ace_gutter {  background: #e8e8e8;  color: #333;}.ace-tomorrow-night-bright .ace_print_margin {  width: 1px;  background: #e8e8e8;}.ace-tomorrow-night-bright .ace_scroller {  background-color: #000000;}.ace-tomorrow-night-bright .ace_text-layer {  cursor: text;  color: #DEDEDE;}.ace-tomorrow-night-bright .ace_cursor {  border-left: 2px solid #9F9F9F;}.ace-tomorrow-night-bright .ace_cursor.ace_overwrite {  border-left: 0px;  border-bottom: 1px solid #9F9F9F;} .ace-tomorrow-night-bright .ace_marker-layer .ace_selection {  background: #424242;}.ace-tomorrow-night-bright .ace_marker-layer .ace_step {  background: rgb(198, 219, 174);}.ace-tomorrow-night-bright .ace_marker-layer .ace_bracket {  margin: -1px 0 0 -1px;  border: 1px solid #343434;}.ace-tomorrow-night-bright .ace_marker-layer .ace_active_line {  background: #2A2A2A;}.ace-tomorrow-night-bright .ace_marker-layer .ace_selected_word {  border: 1px solid #424242;}       .ace-tomorrow-night-bright .ace_invisible {  color: #343434;}.ace-tomorrow-night-bright .ace_keyword {  color:#C397D8;}.ace-tomorrow-night-bright .ace_keyword.ace_operator {  color:#70C0B1;}.ace-tomorrow-night-bright .ace_constant.ace_language {  color:#E78C45;}.ace-tomorrow-night-bright .ace_constant.ace_numeric {  color:#E78C45;}.ace-tomorrow-night-bright .ace_invalid {  color:#CED2CF;background-color:#DF5F5F;}.ace-tomorrow-night-bright .ace_invalid.ace_deprecated {  color:#CED2CF;background-color:#B798BF;}.ace-tomorrow-night-bright .ace_fold {    background-color: #7AA6DA;    border-color: #DEDEDE;}.ace-tomorrow-night-bright .ace_support.ace_function {  color:#7AA6DA;}.ace-tomorrow-night-bright .ace_string {  color:#B9CA4A;}.ace-tomorrow-night-bright .ace_string.ace_regexp {  color:#D54E53;}.ace-tomorrow-night-bright .ace_comment {  color:#969896;}.ace-tomorrow-night-bright .ace_variable {  color:#D54E53;}.ace-tomorrow-night-bright .ace_meta.ace_tag {  color:#D54E53;}.ace-tomorrow-night-bright .ace_entity.ace_other.ace_attribute-name {  color:#D54E53;}.ace-tomorrow-night-bright .ace_entity.ace_name.ace_function {  color:#7AA6DA;}.ace-tomorrow-night-bright .ace_markup.ace_underline {    text-decoration:underline;}.ace-tomorrow-night-bright .ace_markup.ace_heading {  color:#B9CA4A;}";
    var d = a("../lib/dom");
    d.importCssString(b.cssText, b.cssClass)
}), function () {
    ace.require(["ace/ace"], function (a) {
        window.ace || (window.ace = {});
        for (var b in a)a.hasOwnProperty(b) && (ace[b] = a[b])
    })
}()