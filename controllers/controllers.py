from odoo import http
import datetime
from time import strftime, gmtime

class InventoryReport(http.Controller):
	@http.route('/inventory/current/raw', website='True')
	def index(self, **kw):
		stock_quant = http.request.env['stock.inventory.line']
		current_stock = stock_quant.search([])
		context = {
			'real_date' : datetime.datetime.now(),
			'current_stock': current_stock
		}
		return http.request.render('category_variant_inventory_report.show_current_stock', context)

	@http.route('/inventory/current/', auth='public', website='True')
	def current_inventory(self, **kw):
		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_template_id is NULL")
		null_prod_tmpl_id_recs = http.request.env.cr.dictfetchall()
		if null_prod_tmpl_id_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_template_id=(SELECT product_tmpl_id FROM product_product WHERE id=stock_inventory_line.product_id) WHERE product_template_id is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_template_name is NULL")
		null_prod_tmpl_name_recs = http.request.env.cr.dictfetchall()
		if null_prod_tmpl_name_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_template_name=(SELECT name FROM product_template WHERE id=(stock_inventory_line.product_template_id)) WHERE product_template_name is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_attribute_id is NULL")
		null_prod_attr_id_recs = http.request.env.cr.dictfetchall()
		if null_prod_attr_id_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_attribute_id=(SELECT attribute_id FROM product_attribute_line WHERE product_tmpl_id=(stock_inventory_line.product_template_id)) WHERE product_attribute_id is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_attribute_name is NULL")
		null_prod_attr_name_recs = http.request.env.cr.dictfetchall()
		if null_prod_attr_name_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_attribute_name=(SELECT name FROM product_attribute WHERE id=(stock_inventory_line.product_attribute_id)) WHERE product_attribute_name is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_category_id is NULL")
		null_prod_categ_id_recs = http.request.env.cr.dictfetchall()
		if null_prod_categ_id_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_category_id=(SELECT categ_id FROM product_template WHERE id=(stock_inventory_line.product_template_id)) WHERE product_category_id is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_category_name is NULL")
		null_prod_categ_name_recs = http.request.env.cr.dictfetchall()
		if null_prod_categ_name_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_category_name=(SELECT name FROM product_category WHERE id=(stock_inventory_line.product_category_id)) WHERE product_category_name is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_attribute_value_id is NULL")
		null_prod_attr_val_id_recs = http.request.env.cr.dictfetchall()
		if null_prod_attr_val_id_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_attribute_value_id=(SELECT product_attribute_value_id FROM product_attribute_value_product_product_rel WHERE product_product_id=(stock_inventory_line.product_id)) WHERE product_attribute_value_id is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE product_attribute_value_name is NULL")
		null_prod_attr_val_name_recs = http.request.env.cr.dictfetchall()
		if null_prod_attr_val_name_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_attribute_value_name=(SELECT name FROM product_attribute_value WHERE id=(stock_inventory_line.product_attribute_value_id)) WHERE product_attribute_value_name is null;")

		http.request.env.cr.execute("SELECT * from stock_inventory_line WHERE actual_qty is NULL")
		null_prod_actqty_recs = http.request.env.cr.dictfetchall()
		if null_prod_actqty_recs:
			http.request.env.cr.execute("UPDATE public.stock_inventory_line SET actual_qty=(select currentTable.product_qty from (select product_id, MAX(create_date) as create_date from stock_inventory_line group by product_id) as newTable Inner JOIN stock_inventory_line as currentTable ON newTable.product_id = currentTable.product_id AND newTable.create_date = currentTable.create_date WHERE newTable.product_id =(stock_inventory_line.product_id)) where actual_qty is null;")

		http.request.env.cr.execute("SELECT * FROM stock_inventory_line WHERE product_category_fullname is NULL;")
		null_prod_categnames = http.request.env.cr.dictfetchall()
		if null_prod_categnames:
			table = http.request.env['product.category']
			for record in null_prod_categnames:
				db_object = table.search([('id', '=', record['product_category_id'])])
				num_rows = table.search_count([])
				temp_cat_name = []
				for i in range(0,num_rows):
					if db_object.parent_id:
						temp_cat_name.append(db_object.name)
						new_catID = db_object.parent_id.id
						db_object = table.search([('id', '=', new_catID)])
					if not db_object.parent_id:
						temp_cat_name.append(db_object.name)
						break
				temp_cat_name.reverse()
				temp_cat_name = ' / '.join(temp_cat_name)
				http.request.env.cr.execute("UPDATE public.stock_inventory_line SET product_category_fullname=%s", [temp_cat_name])

		http.request.env.cr.execute('''SELECT 
			currentTable.product_id, 
			currentTable.product_template_id, 
			currentTable.product_template_name, 
			currentTable.product_attribute_id, 
			currentTable.product_attribute_name, 
			currentTable.product_category_id, 
			currentTable.product_category_name,  
			currentTable.product_attribute_value_id, 
			currentTable.product_attribute_value_name, 
			currentTable.actual_qty,
			currentTable.product_category_fullname FROM
				(SELECT product_id, MAX(create_date) AS create_date FROM stock_inventory_line GROUP BY product_id) AS newTable INNER JOIN stock_inventory_line AS currentTable ON newTable.product_id = currentTable.product_id AND newTable.create_date = currentTable.create_date ORDER BY product_template_name, product_attribute_value_name;''')
		current_stock = http.request.env.cr.dictfetchall()

		prodIdRecords = []
		for record in (current_stock):
			if not record['product_template_id'] in prodIdRecords:
				prodIdRecords.append(record['product_template_id'])

		variantIdRecords = []
		for record in (current_stock):
			if not record['product_attribute_value_id'] in variantIdRecords:
				variantIdRecords.append(record['product_attribute_value_id'])

		variantNameRecords = []
		for record in (current_stock):
			if not record['product_attribute_value_name'] in variantNameRecords:
				variantNameRecords.append(record['product_attribute_value_name'])

		expectedOutput = []

		for prodId in (prodIdRecords):
			tempArray = []
			i = 0

			for record in (current_stock):
				if prodId == record['product_template_id']:
					if i == 0:
						tempArray.append(record['product_category_fullname'])
						tempArray.append(record['product_template_name'])
						# tempArray.append(record['product_category_name'])
						i+=1
				
			for variantId in (variantIdRecords):
				findVariant = False	
				tempVariantIdRecords = []		
				counter=0	
				for record in (current_stock):
					if prodId == record['product_template_id'] and not variantId in tempVariantIdRecords and variantId == record['product_attribute_value_id']:
						tempArray.append(record['actual_qty'])
						tempVariantIdRecords.append(variantId)
						findVariant = True
					counter+=1	
				if findVariant == False and counter == len(current_stock):
					tempArray.append('0')
					
			expectedOutput.append(tempArray)

		current_date = datetime.datetime.now()
		current_date = strftime("%a, %d-%m-%Y")

		context = {
			'current_date': current_date,
			'variantNameRecords': variantNameRecords,
			'expectedOutput': expectedOutput,
		}
		return http.request.render('category_variant_inventory_report.inventory_current_stock', context)