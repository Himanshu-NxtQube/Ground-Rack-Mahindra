class StackingAnalyzer:
    def __init__(self):
        self.threshold = 1
    
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

    def analyze(self, box_dimensions, stacking_type):
        if not box_dimensions:
            return {"avg_box_length": 0, "avg_box_width": 0, "avg_box_height": 0}

        horizontals = [h for h, _ in box_dimensions]
        verticals = [v for _, v in box_dimensions]

        if stacking_type == "interlock":
            horizontals_sorted = sorted(horizontals)

            # find split in horizontal lengths
            for i in range(len(horizontals_sorted) - 1):
                if horizontals_sorted[i + 1] - horizontals_sorted[i] >= self.threshold:
                    len_group = horizontals_sorted[:i + 1]
                    width_group = horizontals_sorted[i + 1:]

                    avg_len = sum(len_group) / len(len_group)
                    avg_width = sum(width_group) / len(width_group)
                    avg_height = sum(verticals) / len(verticals)

                    return {"avg_box_length": avg_len, "avg_box_width": avg_width, "avg_box_height": avg_height}

            # no clear separation → only length detected
            avg_len = sum(horizontals_sorted) / len(horizontals_sorted)
            avg_height = sum(verticals) / len(verticals)

            return {"avg_box_length": avg_len, "avg_box_width": None, "avg_box_height": avg_height}
        else:
            avg_len = sum(horizontals) / len(horizontals)
            avg_height = sum(verticals) / len(verticals)
            return {"avg_box_length": avg_len, "avg_box_width": None, "avg_box_height": avg_height}

        # box_vertical_len_avg, box_horizontal_len_avg = self.get_avg_dimensions(box_dimensions)
        # stacking_types = []
        # box_lengths = []
        # box_widths = []
        # for box in box_dimensions:
        #     box_horizontal_len = box[0]
        #     box_vertical_len = box[1]

        #     if abs(box_horizontal_len - box_horizontal_len_avg) > 1:
        #         stacking_types.append("interlock")
        #         if box_horizontal_len > box_horizontal_len_avg:
        #             box_lengths.append(int(box_horizontal_len))
        #         else:
        #             box_widths.append(int(box_horizontal_len))
        #     else:
        #         stacking_types.append("normal")

        # stacking_type = max(stacking_types, key=stacking_types.count)

        # if len(box_lengths):
        #     avg_len = sum(box_lengths)/len(box_lengths)
        # else:
        #     avg_len = None
        
        # if len(box_widths):
        #     avg_width = sum(box_widths)/len(box_widths)
        # else:
        #     avg_width = None
        
        # return {"avg_box_length": avg_len, "avg_box_width": avg_width, "avg_box_height": box_vertical_len_avg}

    
