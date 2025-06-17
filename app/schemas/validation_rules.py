import re
from enum import Enum
from typing import Dict, List, Set
from .general_enum import DocumentType
from app.utils.custom_exceptions import ValidationError
class RuleSet(str, Enum):
    general_rules = "general"



general_rules = {
    DocumentType.commercial_invoice: {
    "required_fields": {
        # invoice_info.issuer
        "invoice_info.issuer.name": r"^.+$",  # Non-empty string
        "invoice_info.issuer.address": r"^.+$",  # Non-empty string
        "invoice_info.issuer.cuit": r"^.+$",  # Non-empty string

        # invoice_info
        "invoice_info.date": r"^.+$",  # Non-empty string
        "invoice_info.invoice_number": r"^.+$",  # Non-empty string

        # invoice_to
        "invoice_to.name": r"^.+$",  # Non-empty string
        "invoice_to.address": r"^.+$",  # Non-empty string

        # ship_to
        "ship_to.name": r"^.+$",  # Non-empty string

        # Top-level fields
        "custom_reference": r"^.+$",  # Non-empty string
        "exchange_rate": r"^\d+(\.\d+)?$",  # Float or int, including 0
        "currency": r"^.+$",  # Non-empty string
        "container_number": r"^.+$",  # Non-empty string
        "vessel": r"^.+$",  # Non-empty string
        "final_destination": r"^.+$",  # Non-empty string
        "port_of_loading": r"^.+$",  # Non-empty string
        "shipping_mark": r"^.+$",  # Non-empty string

        # product_table item fields
        "product_table[].code": r"^.+$",  # Non-empty string
        "product_table[].description": r"^.+$",  # Non-empty string
        "product_table[].net_weight_kg": r"^\d+(\.\d+)?$",  # Float or int
        "product_table[].gross_weight_kg": r"^\d+(\.\d+)?$",
        "product_table[].net_weight_lb": r"^\d+(\.\d+)?$",
        "product_table[].gross_weight_lb": r"^\d+(\.\d+)?$",
        "product_table[].units": r"^[1-9]\d*$",  # Positive integer

        # totals
        "totals.total_units": r"^[1-9]\d*$",  # Positive integer
        "totals.total_net_weight_kg": r"^\d+(\.\d+)?$",
        "totals.total_gross_weight_kg": r"^\d+(\.\d+)?$",
        "totals.total_net_weight_lb": r"^\d+(\.\d+)?$",
        "totals.total_gross_weight_lb": r"^\d+(\.\d+)?$",
        "totals.total_fob_value_usd": r"^\d+(\.\d+)?$",
        "totals.freight_port_loading_to_destination_usd": r"^\d+(\.\d+)?$",
        "totals.insurance_port_loading_to_destination_usd": r"^\d+(\.\d+)?$",
        "totals.logistics_service_destination_usd": r"^\d+(\.\d+)?$",
        "totals.freight_port_destination_to_client_usd": r"^\d+(\.\d+)?$",
        "totals.total_value_usd": r"^\d+(\.\d+)?$"
        },
        "cross_field_rules": []
    },

    DocumentType.master_bill_of_lading: {
    "required_fields": {
        # waybill_info
        "waybill_info.issuer.name": r"^.+$",  # Non-empty string
        "waybill_info.issuer.place_of_issue": r"^.+$",  # Non-empty string
        "waybill_info.issuer.date_of_issue": r"^.+$",  # Non-empty string
        "waybill_info.waybill_number": r"^.+$",  # Non-empty string
        "waybill_info.type": r"^.+$",  # Non-empty string

        # shipper
        "shipper.name": r"^.+$",  # Non-empty string
        "shipper.address": r"^.+$",  # Non-empty string

        # consignee
        "consignee.name": r"^.+$",  # Non-empty string
        "consignee.address": r"^.+$",  # Non-empty string

        # booking
        "booking_number": r"^.+$",  # Non-empty string

        # vessel/voyage
        "vessel": r"^.+$",  # Non-empty string
        "voyage_number": r"^.+$",  # Non-empty string

        # ports
        "port_of_loading": r"^.+$",  # Non-empty string
        "port_of_discharge": r"^.+$",  # Non-empty string

        # shipped on board date
        "shipped_on_board_date": r"^.+$",  # Non-empty string

        # containers (multiple fields inside array)
        "containers[].container_number": r"^.+$",  # Non-empty string
        "containers[].seal_number": r"^.+$",  # Non-empty string
        "containers[].container_type": r"^.+$",  # Non-empty string
        "containers[].packages": r"^[1-9]\d*$",  # Positive integer
        "containers[].package_type": r"^.+$",  # Non-empty string
        "containers[].description_of_goods": r"^.+$",  # Non-empty string
        "containers[].total_net_weight_kg": r"^[1-9]\d*(\.\d+)?$",  # Positive number
        "containers[].gross_weight_kg": r"^[1-9]\d*(\.\d+)?$",  # Positive number
        "containers[].cbm": r"^[1-9]\d*(\.\d+)?$",  # Positive number

        # carrier_receipt
        "carrier_receipt.total_containers": r"^[1-9]\d*$",  # Positive integer
        "carrier_receipt.total_packages": r"^[1-9]\d*$",  # Positive integer
        "carrier_receipt.package_type": r"^.+$",  # Non-empty string

        # freight
        "freight_prepaid": r"^(True|False)$",  # Boolean
            }
        },

    DocumentType.one_ocean_master_bill_of_lading: {
        "required_fields": {
            "shipper_exporter.name": r"^.+$",  # Non-empty string
            "shipper_exporter.address": r"^.+$",  # Non-empty string
            "consignee.name": r"^.+$",  # Non-empty string
            "consignee.address": r"^.+$",  # Non-empty string
            "notify_party.name": r"^.+$",  # Non-empty string
            "notify_party.address": r"^.+$",  # Non-empty string
            "booking_no": r"^.+$",  # Non-empty string
            "sea_waybill_no": r"^.+$",  # Non-empty string
            "place_of_receipt": r"^.+$",  # Non-empty string
            "port_of_loading": r"^.+$",  # Non-empty string
            "port_of_discharge": r"^.+$",  # Non-empty string
            "place_of_delivery": r"^.+$",  # Non-empty string
            "vessel.name": r"^.+$",  # Non-empty string
            "vessel.voyage_no": r"^.+$",  # Non-empty string
            "date_of_issue": r"^.+$",  # Non-empty string
            "date_cargo_received": r"^.+$",  # Non-empty string
            "place_of_bill_issue": r"^.+$",  # Non-empty string
            "container_info": r"^.+$",  # Array with at least one valid container object
            "total_cartons": r"^\d+$",  # Integer
            "total_net_weight_kg": r"^\d+(\.\d+)?$",  # Number (int or float)
            "total_gross_weight_kg": r"^\d+(\.\d+)?$",  # Number (int or float)
            "ncm_code": r"^.+$",  # Non-empty string
            "hs_code": r"^.+$",  # Non-empty string
            "seal_sif": r"^.+$",  # Non-empty string
            "ruc": r"^.+$",  # Non-empty string
            "freight_charges": r"^.+$",  # Array with at least one valid object
            "total_prepaid_brl": r"^\d+(\.\d+)?$",  # Number
            "total_prepaid_usd": r"^\d+(\.\d+)?$",  # Number
            "original_bl_count": r"^\d+$",  # Integer
            "is_negotiable": r"^(True|False)$",  # Boolean
            "signed_by": r"^.+$",  # Non-empty string
        }
    },
    DocumentType.packing_list_swift: {
        "required_fields": {
            "exporter.name": r"^.+$",  # Non-empty string
            "exporter.address": r"^.+$",
            "importer.name": r"^.+$",
            "importer.address": r"^.+$",
            "packing_list_number": r"^.+$",
            "vessel": r"^.+$",
            "port_of_loading": r"^.+$",
            "destination_port": r"^.+$",

            # For each item inside a container
            "container_info[].cartons": r"^[1-9]\d*$",  # Integer > 0
            "container_info[].description_of_goods": r"^.+$",
            "container_info[].net_weight_kg": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
            "container_info[].gross_weight_kg": r"^[1-9]\d*(\.\d+)?$",

            # Totals for each container
            "totals.total_net_weight_kg": r"^[1-9]\d*(\.\d+)?$",
            "totals.total_gross_weight_kg": r"^[1-9]\d*(\.\d+)?$",
            "totals.total_cartons": r"^[1-9]\d*$"
        },
        "cross_field_rules": []  # Add cross-field validation rules if needed
    },

    
    DocumentType.argentina_health_certificate:{
         "required_fields": {
                   "certificate_number":r"^.+$",  # Non-empty string,
                    "exporter":r"^.+$",  # Non-empty string,
                    "consignee":r"^.+$",  # Non-empty string,
                    "country_of_origin":r"^.+$",  # Non-empty string,
                    "country_of_destination":r"^.+$",  # Non-empty string,
                    "date_of_issue":r"^.+$",  # Non-empty string,
                    "product_description":r"^.+$",  # Non-empty string,
                    "quantity": r"^[1-9]\d*$",  # Integer > 0,
                    "ministry_authority":r"^.+$",  # Non-empty string,
                    "signature_and_stamp":r"^.+$",  # Non-empty string
                }

    },
    DocumentType.brasil_health_certificate: {
        "required_fields": {
            "exporter": r"^.+$",                    
            "certificate_number": r"^.+$",                             
            "competent_authority": r"^.+$",
            "local_competent_authority": r"^.+$",
            "importer": r"^.+$",
            "country_of_origin": r"^.+$",
            "origin_iso_code": r"^[A-Z]{2,3}$",
            "country_of_dispatch": r"^.+$",
            "dispatch_iso_code": r"^[A-Z]{2,3}$",
            "country_of_destination": r"^.+$",
            "destination_iso_code": r"^[A-Z]{2,3}$",
            "place_of_loading": r"^.+$",
            "means_of_transport": r"^.+$",
            "point_of_entry": r"^.+$",
            "conditions_for_transport_storage": r"^.+$",
            "container_seal_numbers": r"^.+$",
            "shipping_marks": r"^.+$",
            "food_producers": r"^.+$",
            "purpose": r"^.+$",
            "ncm_hs_code": r"^\d{4,10}$",  # Adjusted for common NCM/HS code lengths
            "certificate_reference_number": r"^.+$",
            "carteira_fiscal_number": r"^.+$",

            "product_details[].product_description": r"^.+$",
            "product_details[].animal_species": r"^.+$",
            "product_details[].lot_or_production_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date
            "product_details[].slaughter_date": r"^\d{4}-\d{2}-\d{2}$",         # ISO date
            "product_details[].producer_approval_number": r"^.+$",
            "product_details[].type_of_packaging": r"^.+$",
            "product_details[].number_of_packages": r"^\d+$",
            "product_details[].net_weight_kgs": r"^\d+([.,]\d+)?$",
            "product_details[].net_weight_lbs": r"^\d+([.,]\d+)?$"
        }
    },
    DocumentType.brasil_master_bill_of_lading:{
         "required_fields": {
            "bill_of_lading_no": r"^.+$",                    # non-empty string
            "shipper": r"^.+$",                              # non-empty string
            "consignee": r"^.+$",                            # non-empty string
            "notify_parties": r"^.+$",                        # non-empty string
            "vessel_and_voyage_no": r"^.+$",                  # non-empty string
            "port_of_loading": r"^.+$",                        # non-empty string
            "port_of_discharge": r"^.+$",                      # non-empty string
            "container_numbers": r"^.+$",                      # string inside array, each item non-empty
            "description_of_packages_and_goods": r"^.+$",     # non-empty string
            "gross_cargo_weight": r"^[\d.,\s]+$",              # numbers, dots, commas, spaces (e.g. "17,012.50")
            "total_items": r"^\d+$",                            # integer (digits only)
            "total_gross_weight": r"^[\d.,\s]+$",              # numbers, dots, commas, spaces
            "net_weight": r"^[\d.,\s]+$",                       # numbers, dots, commas, spaces
            "gross_weight": r"^[\d.,\s]+$",                     # numbers, dots, commas, spaces
            "shipped_on_board_date": r"^\d{4}-\d{2}-\d{2}$",   # date YYYY-MM-DD
            "freight_charges": {
                "rate": r"^[\d.,\s]+$",                           # numbers, dots, commas, spaces
                "prepaid": r"^.+$",                               # non-empty string
                "collect": r"^.+$",                               # non-empty string
                "terminal_handling_charge": r"^[\d.,\s]+$"        # numbers, dots, commas, spaces
            },
            "place_and_date_of_issue": r"^.+$",                 # non-empty string
            "container_cargo_table[].container_numbers": r"^.+$",
            "container_cargo_table[].seal_numbers": r"^.+$",
            "container_cargo_table[].marks_and_numbers": r"^.+$",
            "container_cargo_table[].description_of_packages_and_goods": r"^.+$",
            "container_cargo_table[].gross_cargo_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].measurement": r"^.+$",
            "container_cargo_table[].net_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].gross_weight": r"^[\d.,\s]+$",
            "container_cargo_table[].ncm": r"^.+$",
            "container_cargo_table[].hs_code": r"^.+$",
            "container_cargo_table[].seal_sif": r"^.+$",
            "container_cargo_table[].temperature": r"^.+$",
            "container_cargo_table[].ruc": r"^.+$",   
        }
    },
    DocumentType.nop_import_certificate: {
        "required_fields": {
            "certificate_type": r"^.+$",  # Non-empty string
            "issuing_agency": r"^.+$",  # Non-empty string
            "import_certificate_number": r"^.+$",  # Non-empty string
            "date_of_issue": r"^.+$",  # Non-empty string
            "certifying_body_issuing_certificate.name": r"^.+$",  # Non-empty string
            "certifying_body_issuing_certificate.address": r"^.+$",  # Non-empty string
            "certifying_body_of_final_handler.name": r"^.+$",  # Non-empty string
            "certifying_body_of_final_handler.address": r"^.+$",  # Non-empty string
            "recipient_us.name": r"^.+$",  # Non-empty string
            "recipient_us.address": r"^.+$",  # Non-empty string
            "recipient_us.contact.person": r"^.+$",  # Non-empty string
            "recipient_us.contact.email": r"^.+$",  # Non-empty string
            "recipient_us.contact.phone": r"^.+$",  # Non-empty string
            "city_state_product_destination": r"^.+$",  # Non-empty string
            "total_net_weight_kg": r"^[0-9]+(\.[0-9]+)?$",  # Positive number (integer or float)
            "total_containers": r"^[1-9]\d*$",  # Integer > 0
            "product_exported_from": r"^.+$",  # Non-empty string
            "remarks_attestations": r"^.+$",  # Non-empty string
            "signature_of_certifying_body": r"^.+$",  # Non-empty string
            "signature_date": r"^.+$",  # Non-empty string

            # For each product item (required subfields)
            "product[].description": r"^.+$",  # Non-empty string
            "product[].harmonized_tariff_code": r"^.+$",  # Non-empty string
            "product[].shipping_identification": r"^.+$",  # Non-empty string
            "product[].final_handler.name": r"^.+$",  # Non-empty string
            "product[].final_handler.address": r"^.+$",  # Non-empty string
            "product[].final_handler.contact.person": r"^.+$",  # Non-empty string
            "product[].final_handler.contact.email": r"^.+$",  # Non-empty string
            "product[].final_handler.contact.phone": r"^.+$",  # Non-empty string
        }
    },

    DocumentType.packing_list_minerva: {
        "required_fields": {
            "packing_list_number": r"^.+$",  # Non-empty string
            "date": r"^.+$",  # Non-empty string

            "exporter.name": r"^.+$",  # Non-empty string
            "exporter.address": r"^.+$",  # Non-empty string

            "importer.name": r"^.+$",  # Non-empty string
            "importer.address": r"^.+$",  # Non-empty string

            "ocean_vessel": r"^.+$",  # Non-empty string
            "port_of_loading": r"^.+$",  # Non-empty string
            "port_of_discharge": r"^.+$",  # Non-empty string
            "shipping_mark": r"^.+$",  # Non-empty string

            # For each item in goods array
            "goods[].container_type": r"^.+$",  # Non-empty string
            "goods[].description": r"^.+$",  # Non-empty string
            "goods[].net_weight_kg": r"^\d+(\.\d+)?$",  # Number
            "goods[].gross_weight_kg": r"^\d+(\.\d+)?$",  # Number
            "goods[].cartons": r"^\d+$",  # Integer
            "goods[].container_number": r"^.+$",  # Non-empty string

            # Totals
            "total.net_weight_kg": r"^\d+(\.\d+)?$",  # Number
            "total.gross_weight_kg": r"^\d+(\.\d+)?$",  # Number
            "total.cartons": r"^\d+$",  # Integer
            }
        },
        DocumentType.certificate_of_origin: {
            "required_fields": {
                "product_code": r"^.+$",  # Non-empty string
                "product_description": r"^.+$",  # Non-empty string
                "shipping_mark": r"^.+$",  # Non-empty string
                "brand": r"^.+$",  # Non-empty string
                "vessel": r"^.+$",  # Non-empty string
                "destination": r"^.+$",  # Non-empty string
                "container_number": r"^.+$",  # Non-empty string
                "total_units": r"^[1-9]\d*$",  # Integer > 0
                "net_weight_kg": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
                "gross_weight_kg": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
                "microbiological_analysis[].production_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
                "microbiological_analysis[].cartons": r"^[1-9]\d*$",  # Integer > 0
                "microbiological_analysis[].lot_number": r"^.+$",  # Non-empty string
                "microbiological_analysis[].salmonella_in_325g": r"^.+$",  # Non-empty string
                "microbiological_analysis[].top_seven_stecs_in_325g": r"^.+$",  # Non-empty string
                "laboratory.name": r"^.+$",  # Non-empty string
                "laboratory.address": r"^.+$",  # Non-empty string
                "certifier.organization": r"^.+$",  # Non-empty string
                "certifier.name": r"^.+$",  # Non-empty string
                "date_of_issue": r"^\d{4}-\d{2}-\d{2}$"  # ISO date format
            },
            "cross_field_rules": []
        },

    DocumentType.certificate_of_analysis : {
        "required_fields": {
            "product_code": r"^.+$",
            "shipping_mark": r"^.+$",
            "brand": r"^.+$",
            "vessel": r"^.+$",
            "destination": r"^.+$",
            "container_number": r"^.+$",
            "total_units": r"^[1-9]\d*$",  # positive integers only
            "net_weight_kg": r"^\d+(\.\d+)?$",  # positive float or integer
            "gross_weight_kg": r"^\d+(\.\d+)?$",  # positive float or integer
            "date_of_issue": r"^.+$",

            # Nested fields for microbiological_analysis
            "microbiological_analysis[].production_date": r"^.+$",
            "microbiological_analysis[].cartons": r"^[1-9]\d*$",
            "microbiological_analysis[].lot_number": r"^.+$",
            "microbiological_analysis[].salmonella_in_325g": r"^.+$",
            "microbiological_analysis[].top_seven_stecs_in_325g": r"^.+$",

            # Nested fields for laboratory
            "laboratory.name": r"^.+$",
            "laboratory.address": r"^.+$",

            # Nested fields for certifier
            "certifier.organization": r"^.+$",
            "certifier.name": r"^.+$"
            }
    },
    DocumentType.brasil_isf: {
        "required_fields": {
            "seller_name_address": r"^.+$",
            "buyer_name_address": r"^.+$",
            "ship_to_party": r"^.+$",
            "container_stuffing_location": r"^.+$",
            "importer_of_record": r"^.+$",
            "manufacturer_name_address": r"^.+$",
            "consignee": r"^.+$",
            "country_of_origin": r"^.+$",
            "commodity_description": r"^.+$",
            "vessel_voyage": r"^.+$",
            "bill_of_lading_number": r"^.+$",
            "container_number": r"^[A-Z]{4}\d{7}$",  # Standard container number format (e.g., ABCD1234567)
            "etd": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
            "eta": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
        }
    },
    DocumentType.brasil_certificate_of_analysis: {
        "required_fields": {
            "loaded_date": r"^\d{4}-\d{2}-\d{2}$",             # ISO date format (YYYY-MM-DD)
            "container_number": r"^[A-Z]{4}\d{7}$",            # Standard container number format (ABCD1234567)
            "shipping_mark": r"^.+$",                          # Non-empty string
            "customer": r"^.+$",                               # Non-empty string
            "destination": r"^.+$",                            # Non-empty string
            "contract_number": r"^.+$",                        # Non-empty string
            "net_weight_kg": r"^\d{1,3}(\.\d{3})*,\d{2}$",                 # Positive float or integer
            "microbiological_results[].product_code": r"^.+$",
            "microbiological_results[].batch_lot": r"^.+$",
            "microbiological_results[].result_ecoli_o157_h7": r"^.+$",
            "microbiological_results[].result_salmonella": r"^.+$"		
        }
    },
    DocumentType.brasil_commercial_invoice: {
        "required_fields": {
           "document_type": r"^.+$",
            "issuing_country": r"^.+$",
            "fields.invoice_number": r"^.+$",
            "fields.invoice_date": r"^\d{4}-\d{2}-\d{2}$",
            "fields.importer_details": r"^.+$",
            "fields.ocean_vessel": r"^.+$",
            "fields.port_of_loading": r"^.+$",
            "fields.port_of_discharge": r"^.+$",
            "fields.payment_terms": r"^.+$",
            "fields.importer_ref": r"^.+$",
            "fields.shipping_mark": r"^.+$",
            "fields.signer_cpf": r"^.+$",

            "tables.line_items[].description_of_goods": r"^.+$",
            "tables.line_items[].net_weight_kgs": r"^\d+(\.\d+)?$",
            "tables.line_items[].unit_price_usd_per_kgs": r"^\d+(\.\d+)?$",
            "tables.line_items[].amount_usd": r"^\d+(\.\d+)?$",

            "tables.totals[].description": r"^.+$",
            "tables.totals[].currency": r"^[A-Z]{3}$",  # e.g., USD, BRL
            "tables.totals[].amount": r"^\d+(\.\d+)?$",

            "tables.container_details[].container_id": r"^.+$",
            "tables.container_details[].net_weight_details": r"^.+$",
            "tables.container_details[].gross_weight_details": r"^.+$",
            "tables.container_details[].carton_count": r"^\d+$",

            "banking_details.intermediary_bank": r"^.+$",
            "banking_details.intermediary_aba": r"^.+$",
            "banking_details.intermediary_swift": r"^[A-Z0-9]{8,11}$",
            "banking_details.beneficiary_bank": r"^.+$",
            "banking_details.beneficiary_bank_address": r"^.+$",
            "banking_details.beneficiary_swift": r"^[A-Z0-9]{8,11}$",
            "banking_details.beneficiary_account_number": r"^.+$",
            "banking_details.beneficiary_name": r"^.+$"
        }
    },
    DocumentType.brasil_certificate_of_origin: {
        "required_fields": {
            "document_type": r"^.+$",  # string
            "issuing_country": r"^.+$",  # string
            "fields.certificate_number": r"^.+$",  # string
            "fields.exporter": r"^.+$",  # string
            "fields.importer": r"^.+$",  # string
            "fields.importer_ref": r"^.+$",  # string
            "fields.shipping_mark": r"^.+$",  # string
            "fields.vessel": r"^.+$",  # string
            "fields.shipment_port": r"^.+$",  # string
            "fields.destination": r"^.+$",  # string
            "fields.total_net_weight_kgs_summary": r"^\d+(\.\d+)?$",  # number
            "fields.total_gross_weight_kgs_summary": r"^\d+(\.\d+)?$",  # number
            "fields.total_cartons_summary": r"^\d+$",  # integer
            "fields.container_id_summary": r"^.+$",  # string
            "fields.total_weight": r"^\d+(\.\d+)?$",  # number
            "fields.signer_cpf": r"^.+$",  # string
            "fields.issue_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format
            "fields.issue_location": r"^.+$",  # string
            "tables.goods_description[].cartons": r"^\d+$",  # integer
            "tables.goods_description[].description": r"^.+$",  # string
            "tables.goods_description[].net_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "tables.container_details[].container_id": r"^.+$",  # string
            "tables.container_details[].net_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "tables.container_details[].gross_weight_kgs": r"^\d+(\.\d+)?$",  # number
            "tables.container_details[].cartons": r"^\d+$"  # integer
        }
    },
    DocumentType.brasil_certificate_of_origin: {
        "required_fields": {
             "document_type": r"^.+$",
            "issuing_country": r"^.+$",
            "fields.certificate_number": r"^.+$",
        }
    },
    DocumentType.air_waybill: {
        "required_fields": ["mawb", "hawb", "gross_weight", "shipper"],
        "dangerous_goods": {
            "un_number_format": r"^UN\d{4}$",
            "allowed_hazard_classes": ["3", "4", "8", "9"],
            "prohibited_materials": [
                "explosives", 
                "radioactive_materials"
            ]
        },
        "weight": {
            "unit": "kg",
            "max_value": 1000  # kg
        },
        "special_handling_codes": [
            "FRAGILE", "PERISHABLE", "THIS_SIDE_UP"
        ]
    }, 
    DocumentType.dangerous_goods: {
        "required_fields": ["un_number", "proper_shipping_name", "emergency_contacts"],
        "packaging_standards": {
            "container_types": ["1A1", "1A2", "4G"],
            "max_quantity_per_package": 1000  # liters/kg based on class
        },
        "emergency_info": {
            "required_contacts": 2,
            "24hr_contact": True
        }
    },
    DocumentType.abf_freight_invoice:{
        "required_fields": {
                "invoice_number": r"^.+$",  # Non-empty string
                "pro_number": r"^.+$",      # Non-empty string
                "total_invoice_amount_usd": r"^[1-9]\d*(\.\d+)?$",  # Float > 0
                "reference_numbers.po_number": r"^.+$",  # Non-empty string
                "reference_numbers.bill_of_lading_number": r"^.+$",  # Non-empty string
                "ship_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
                "invoice_due_date": r"^\d{4}-\d{2}-\d{2}$",  # ISO date format YYYY-MM-DD
                "total_piece_count": r"^[1-9]\d*$",  # Integer > 0
                "total_weight_lbs": r"^[1-9]\d*$",  # Integer > 0
                "weight_lbs": r"^[1-9]\d*$",  # Integer > 0
                "piece_count": r"^[1-9]\d*$"  # Integer > 0
            },
            "cross_field_rules": []
    }       
}

PROHIBITED_MATERIALS: Set[str] = {
    "explosives", "radioactive_materials", "chemical_weapons"
}

def get_validation_rules(doc_type: DocumentType, rule_set: RuleSet) -> Dict:
    """Get compliance rules for document type and regulation set"""
    rule_map = {
        RuleSet.general_rules: general_rules
    }
    return rule_map[rule_set].get(doc_type, {})

def validate_un_number_format(un_number: str) -> bool:
    """Validate UN number against IATA/IMO format requirements"""
    return re.match(r"^UN\d{4}$", un_number) is not None

def check_prohibited_materials(description: str) -> List[str]:
    """Check material descriptions against global prohibited list"""
    return [
        material for material in PROHIBITED_MATERIALS 
        if material in description.lower()
    ]
 

def validate_against_rules(data: Dict, doc_type: DocumentType, rule_set: RuleSet) -> Dict:
    """Main validation entry point"""
    rules = get_validation_rules(doc_type, rule_set)
    #result_errors = ErrorValidationRules()
    errors = []

    # Check required fields
    missing_fields = [
        field for field in rules.get("required_fields", [])
        if field not in data or data[field] is None
    ]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")

    # Document-type specific validations
    if doc_type == DocumentType.air_waybill:
        if "dangerous_goods" in data:
            dg_data = data["dangerous_goods"]
            if not validate_un_number_format(dg_data.get("un_number", "")):
                errors.append("Invalid UN number format")
            
            if prohibited := check_prohibited_materials(dg_data.get("description", "")):
                errors.append(f"Prohibited materials: {', '.join(prohibited)}")

    elif doc_type == DocumentType.dangerous_goods:
        # IMO-specific validations
        pass

    if errors:
        raise ValidationError(errors,doc_type=doc_type,ocr_mapped_fields=data)
    
    return data


def validate_single_field(schema_class, field_name: str, value):
    try:
        # Create partial input with just the field to validate
        validated = schema_class(**{field_name: value})
        return 1.0, "OK"
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        return 0.5, f"Validation error: {error_msg}"
    
# score, reason = validate_single_field(DangerousGoodsSchema, "un_number", "UN1234")
# print(score, reason)  # Output: 1.0, OK