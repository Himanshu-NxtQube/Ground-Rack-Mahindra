import os
import pymysql
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.utils.s3_operator import upload_images
from src.utils.rds_operator import RDSOperator

rds_operator = RDSOperator()
conn = pymysql.connect(
    host=os.getenv("rds_host"),  # RDS Endpoint
    user=os.getenv("rds_user"),                    # DB username
    password=os.getenv("rds_password"),                # DB password
    database=os.getenv("rds_dbname"),           # Target DB name
    port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
)

def insert_record(image_name, rack_id, box_number, invoice_number, box_quantity, part_number, image_obj_key_id, unique_id="", user_id=14, exclusion="", barcode=""):
    try:
        with conn.cursor() as cursor:
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

with conn.cursor() as cursor:
    # records = [
    #     # DJI_0012.JPG
    #     [
    #         "DJI_0012.JPG",
    #         "HD-02/A/32", "", "", "", "", "empty rack",
    #         "HD-02/A/31", "1805AW50001N", "24", "NA", "FULL", ""
    #     ],

    #     # DJI_0013.JPG
    #     [
    #         "DJI_0013.JPG",
    #         "HD-02/A/30", "1805AW00011N", "36", "NA", "FULL", "",
    #         "HD-02/A/29", "1805AW00011N", "37", "NA", "Partial", ""
    #     ],

    #     # DJI_0014.JPG
    #     [
    #         "DJI_0014.JPG",
    #         "HD-02/A/28", "1805AAA07851N", "53", "NA", "Partial", "",
    #         "HD-02/A/27", "1805AAA07851N", "58", "NA", "Partial", ""
    #     ],

    #     # DJI_0020.JPG
    #     [
    #         "DJI_0020.JPG",
    #         "HD-04/A/34", "", "", "NA", "NA", "empty rack",
    #         "HD-04/A/33", "1301EW500111N", "16", "NA", "FULL", ""
    #     ],

    #     # DJI_0022.JPG
    #     [
    #         "DJI_0022.JPG",
    #         "HD-04/A/28", "2301EW5G0090N", "12", "NA", "FULL", "",
    #         "HD-04/A/27", "2301EW5G0090N", "12", "NA", "FULL", ""
    #     ],

    #     # DJI_0720.JPG
    #     [
    #         "DJI_0720.JPG",
    #         "HD-02/A/02", "", "", "NA", "NA", "empty rack",
    #         "HD-02/A/01", "1805AS200221N", "48", "NA", "FULL", ""
    #     ],

    #     # DJI_0721.JPG
    #     [
    #         "DJI_0721.JPG",
    #         "HD-02/A/04", "1805AS200221N", "44", "NA", "Partial", "",
    #         "HD-02/A/03", "", "", "NA", "NA", "empty rack"
    #     ],

    #     # DJI_0722.JPG
    #     [
    #         "DJI_0722.JPG",
    #         "HD-02/A/06", "1805AS200221N", "56", "NA", "Full", "",
    #         "HD-02/A/05", "1805AS200221N", "39", "NA", "Partial", ""
    #     ],

    #     # DJI_0725.JPG
    #     [
    #         "DJI_0725.JPG",
    #         "HD-02/A/16", "1805AAA07681N", "42", "NA", "Full", "",
    #         "HD-02/A/15", "1805AAA07681N", "23", "NA", "Partial", ""
    #     ],

    #     # DJI_0729.JPG
    #     [
    #         "DJI_0729.JPG",
    #         "HD-02/A/28", "1805AAA07851N", "46", "NA", "Partial", "",
    #         "HD-02/A/27", "1805AAA07851N", "60", "NA", "Full", ""
    #     ],

    #     # DJI_0730.JPG
    #     [
    #         "DJI_0730.JPG",
    #         "HD-02/A/30", "1805AW500011N", "42", "NA", "Full", "",
    #         "HD-02/A/29", "1805AW500011N", "37", "NA", "Partial", ""
    #     ],

    #     # DJI_0731.JPG
    #     [
    #         "DJI_0731.JPG",
    #         "HD-02/A/34", "1805AW500061N", "51", "NA", "Partial", "",
    #         "HD-02/A/33", "1805AW500061N", "36", "NA", "Full", ""
    #     ],

    #     # DJI_0732.JPG
    #     [
    #         "DJI_0732.JPG",
    #         "HD-02/A/36", "1305AW500061N", "71", "NA", "Partial", "",
    #         "HD-02/A/35", "1305AW500061N", "60", "NA", "Full", ""
    #     ],

    #     # DJI_0740.JPG
    #     [
    #         "DJI_0740.JPG",
    #         "HD-04/A/10", "2301EAG00081S", "12", "NA", "Full", "",
    #         "HD-04/A/09", "2301EAG00081S", "12", "NA", "Full", ""
    #     ],

    #     # DJI_0741.JPG
    #     [
    #         "DJI_0741.JPG",
    #         "HD-04/A/12", "2301EAG00081S", "16", "NA", "Full", "",
    #         "HD-04/A/11", "", "", "NA", "", "empty rack"
    #     ],
    # ]
    records = [
        [
            "DJI_0019.JPG",
            "HD-02/A/34", "", "", "", "", "empty rack",
            "HD-02/A/33", "1805AW500061N", "20", "NA", "Partial", ""
        ]
    ]
    report_id = rds_operator.create_report(conn, 14)
    # format
    # [image_name, rack_id_left, left_part_number, left_box_number, left_box_quantity, left_invoice, left_exclusion, right_rack_id, right_part_number, right_box_number, right_box_quantity, right_invoice, right_exclusion]
    for record in records:
        image_name = record[0]
        image_path = os.path.join("images", image_name)
        s3_key, s3_url = upload_images(image_path)
        key_id = rds_operator.store_img_info(image_path, conn)
        

        # left
        insert_record(image_name=image_name, image_obj_key_id=key_id, rack_id=record[1], part_number=record[2], box_number=record[3], box_quantity=record[4], invoice_number=record[5], exclusion=record[6], user_id=14)
        # right
        insert_record(image_name=image_name, image_obj_key_id=key_id, rack_id=record[7], part_number=record[8], box_number=record[9], box_quantity=record[10], invoice_number=record[11], exclusion=record[12], user_id=14)
            
