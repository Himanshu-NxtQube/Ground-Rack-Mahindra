import pymysql
import os

class RDSInsertData:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("rds_host"),  # RDS Endpoint
            user=os.getenv("rds_user"),                    # DB username
            password=os.getenv("rds_password"),                # DB password
            database=os.getenv("rds_dbname"),           # Target DB name
            port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
        )
    
    def insert_record(self, image_name, report_id, rack_id, box_number, invoice_number, box_quantity, part_number, image_obj_key_id, unique_id="", user_id=14, exclusion="", barcode=""):
        try:
            with self.conn.cursor() as cursor:
                # --- Check for existing record ---
                if unique_id == None:
                    check_query = """
                    SELECT id FROM inferances
                    WHERE uniqueId = %s AND userId = %s AND barcode_number = %s
                    """
                    check_values = (unique_id, user_id, barcode)  # userId is hardcoded to 3

                    cursor.execute(check_query, check_values)
                    existing = cursor.fetchone()
                else:
                    existing = False

                # is_non_conformity = True if exclusion[:5] == "There" else False
                is_non_conformity = exclusion not in ("empty rack", "", "Predicted")
                status = None

                if existing:
                    # --- Update existing record ---
                    update_query = """
                    UPDATE inferances
                    SET
                        image_name = %s, rack_id = %s, box_number = %s, invoice_number = %s,
                        box_quantity = %s, part_number = %s, exclusion = %s, status = %s,
                        is_non_conformity = %s, isDispatched = %s, isDeleted = %s,
                        isReplishment = %s, reportId = %s, imageObjKeyId = %s
                    WHERE id = %s
                    """
                    update_values = (
                        image_name, 
                        rack_id if not rack_id else "", 
                        box_number if not box_number else "", 
                        invoice_number if not invoice_number else "",
                        box_quantity if not box_quantity else "", 
                        part_number if not part_number else "", 
                        exclusion, 
                        status,
                        is_non_conformity, 
                        False, 
                        False, 
                        False, 
                        report_id, 
                        image_obj_key_id, 
                        existing[0]
                    )
                    cursor.execute(update_query, update_values)
                    print(f"Updated record with id = {existing[0]}")
                else:
                    # --- Insert new record ---
                    insert_query = """
                    INSERT INTO inferances (
                        uniqueId, barcode_number, image_name, rack_id, box_number,
                        invoice_number, box_quantity, part_number, exclusion, status,
                        is_non_conformity, isDispatched, isDeleted, isReplishment,
                        reportId, imageObjKeyId, userId
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    """
                    insert_values = (
                        unique_id if unique_id else "", 
                        barcode if barcode else "", 
                        image_name,
                        rack_id if rack_id else "", 
                        box_number if box_number else "", 
                        invoice_number if invoice_number else "",
                        box_quantity if box_quantity else "", 
                        part_number if part_number else "",
                        exclusion, 
                        status,
                        is_non_conformity, 
                        False, 
                        False, 
                        False,
                        report_id, 
                        image_obj_key_id, 
                        user_id
                    )
                    cursor.execute(insert_query, insert_values)
                    print("Inserted new record.")

                conn.commit()

        except Exception as e:
            print("Insert/Update unsuccessful:", e)