label_mapping = {
    0: "GOOD",
    1: "ng_jahit_loncat",
    2: "ng_noda",
    3: "ng_pucker",
    4: "ng_robek",
    5: "ng_tepi_tidak_rapi"
}

def decode_prediction(pred):
    return label_mapping.get(pred, "Unknown")