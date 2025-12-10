class StackingAnalyzer:
    def get_avg_dimensions(self, boxes):
        if len(boxes)==0:
            return 0,0
        box_horizontal_len_sum = 0
        box_vertical_len_sum = 0
        for box in boxes:
            box_horizontal_len = box[0]
            box_vertical_len = box[1]

            box_horizontal_len_sum += box_horizontal_len
            box_vertical_len_sum += box_vertical_len

        box_vertical_len_avg = box_vertical_len_sum/len(boxes)
        box_horizontal_len_avg = box_horizontal_len_sum/len(boxes)
        return box_vertical_len_avg, box_horizontal_len_avg

    def analyze(self, box_dimensions):
        if len(box_dimensions)==0:
            return {"stacking_type": "empty", "avg_box_length": 0, "avg_box_width": 0, "avg_box_height": 0}

        box_vertical_len_avg, box_horizontal_len_avg = self.get_avg_dimensions(box_dimensions)
        stacking_types = []
        box_lengths = []
        box_widths = []
        for box in box_dimensions:
            box_horizontal_len = box[0]
            box_vertical_len = box[1]

            if abs(box_horizontal_len - box_horizontal_len_avg) > 1:
                stacking_types.append("interlock")
                if box_horizontal_len > box_horizontal_len_avg:
                    box_lengths.append(int(box_horizontal_len))
                else:
                    box_widths.append(int(box_horizontal_len))
            else:
                stacking_types.append("normal")

        stacking_type = max(stacking_types, key=stacking_types.count)

        if len(box_lengths):
            avg_len = sum(box_lengths)/len(box_lengths)
        else:
            avg_len = None
        
        if len(box_widths):
            avg_width = sum(box_widths)/len(box_widths)
        else:
            avg_width = None
        
        return {"stacking_type": stacking_type, "avg_box_length": avg_len, "avg_box_width": avg_width, "avg_box_height": box_vertical_len_avg}

    