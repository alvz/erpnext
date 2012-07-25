// ERPNext - web based ERP (http://erpnext.com)
// Copyright (C) 2012 Web Notes Technologies Pvt Ltd
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

cur_frm.cscript.refresh = function(doc) {
	cur_frm.toggle_display('attach', doc.rename_doctype && !doc.file_list);
	cur_frm.toggle_display('rename', doc.file_list);
}

cur_frm.cscript.rename_doctype = function(doc) {
	cur_frm.cscript.refresh(doc);
}

cur_frm.cscript.attach = function(doc) {
	cur_frm.attachments.add_attachment();
}

cur_frm.fields_dict.rename_doctype.get_query = function() {
	return "select name from tabDocType where %(key)s like '%s%%' and ifnull(allow_rename,0)=1"
}