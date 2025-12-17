import regex
import matplotlib.pyplot as plt
import cv2

class RackBoxExtractor:
    def __init__(self):
        
        self.area_threshold = 4000

    
    
    
    
    def extract_rack_info(self, annotations, boundaries, image_dims):
        self.center_x = image_dims[0]/2
        self.center_y = image_dims[1]/2
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries

        # all_rack_ids = []
        left_rack_ids = []
        right_rack_ids = []
        Q1_rack_ids, Q2_rack_ids, Q3_rack_ids, Q4_rack_ids = [],[],[],[]
        rack_dict = {}

        pattern = regex.compile("^HD-(0[1-9]|1[0-9]|2[0-6])/([A-Z])/(0[1-9]|1[0-9]|2[0-9]|3[0-8])$")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # TODO: Remove tuples or list and use Dict(s) 
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - 


        # for annotation in annotations:
        #     text = annotation.description
        #     print("TEXT : ", text)
        #     vertices = annotation.bounding_poly.vertices

        #     text_center_x = sum([v.x for v in vertices])/4
        #     text_center_y = sum([v.y for v in vertices])/4


        #     x_coords = [v.x for v in vertices]
        #     y_coords = [v.y for v in vertices]

        #     width = max(x_coords) - min(x_coords)
        #     height = max(y_coords) - min(y_coords)

        #     text_area = width * height
        #     # Ensuring its within ROI and matches the regex pattern
        #     if (left_line_x < text_center_x < right_line_x) and text_area > self.area_threshold and re.match(pattern, text):
        #         print("Text:", text, "Area:", text_area)
        #         if text_center_x < self.center_x:
        #             left_rack_ids.append((text,text_center_y))
        #         else:
        #             right_rack_ids.append((text,text_center_y))
        
        # for rack_id, text_center_y in left_rack_ids:
        #     if text_center_y < self.center_y:
        #         Q2_rack_ids.append((rack_id, text_center_y))
        #     else:
        #         Q3_rack_ids.append((rack_id, text_center_y))

        # for rack_id, text_center_y in right_rack_ids:
        #     if text_center_y < self.center_y:
        #         Q1_rack_ids.append((rack_id, text_center_y))
        #     else:
        #         Q4_rack_ids.append((rack_id, text_center_y))
        
        # Q1_rack_id = (min(Q1_rack_ids, key=lambda x:x[1])[0], 'Q1') if Q1_rack_ids else None
        # Q2_rack_id = (min(Q2_rack_ids, key=lambda x:x[1])[0], 'Q2') if Q2_rack_ids else None
        # Q3_rack_id = (max(Q3_rack_ids, key=lambda x:x[1])[0], 'Q3') if Q3_rack_ids else None
        # Q4_rack_id = (max(Q4_rack_ids, key=lambda x:x[1])[0], 'Q4') if Q4_rack_ids else None

        # if Q1_rack_id:
        #     all_rack_ids.append(Q1_rack_id) 
        # if Q2_rack_id:
        #     all_rack_ids.append(Q2_rack_id) 
        # if Q3_rack_id:
        #     all_rack_ids.append(Q3_rack_id) 
        # if Q4_rack_id:
        #     all_rack_ids.append(Q4_rack_id) 

        # # print(all_rack_ids)
            
        # return all_rack_ids


        i = 0
        exp_len = 10
        res = []
        n = len(annotations)
        while i < n:
            annotation = annotations[i]
            text = annotation.description
            if text[0] == '1':
                text = 'I' + text[1:]
            # print("text:",text)

            if pattern.fullmatch(text):
                center, area = self.compute_bbox([annotation.bounding_poly.vertices])
                res.append({'rack_id':text, 'center': center, 'area': area})
                continue
            
            if len(text) >= exp_len:
                text = text[:exp_len]
                if pattern.fullmatch(text):
                    center, area = self.compute_bbox([annotation.bounding_poly.vertices])
                    res.append({'rack_id':text, 'center': center, 'area': area})
                i+=1
                continue

            match = pattern.match(text, partial=True)
            if match and match.partial:
                # group_verts = list(annotation.bounding_poly.vertices)
                group_verts = [annotation.bounding_poly.vertices]
                combined = text
                j = i + 1
                while len(combined) < exp_len and j < n and not pattern.fullmatch(combined):
                    nxt = annotations[j]
                    combined += nxt.description.strip()
                    group_verts.append(nxt.bounding_poly.vertices)
                    # print("combined",combined)
                    j += 1
                combined = combined[:exp_len]
                # print("After trim:",combined)
                if pattern.fullmatch(combined):
                    center, area = self.compute_bbox(group_verts)
                    # print('-'*15 + '\n')
                    # print("FOUND:", combined)
                    # print('\n' + '-'*15)
                    res.append({'rack_id': combined, 'center': center, 'area': area})
                    i = j
                    continue
                combined = combined[:-1]
                if pattern.fullmatch(combined):
                    center, area = self.compute_bbox(group_verts)
                    # print('-'*15 + '\n')
                    # print("FOUND:", combined)
                    # print('\n' + '-'*15)
                    res.append({'rack_id': combined, 'center': center, 'area': area})
                    i = j
                    continue
            i += 1

        for rack_info in res:
            rack_id = rack_info['rack_id']
            text_center_x, text_center_y = rack_info['center']
            text_area = rack_info['area']
            # print("Rack ID:",rack_id, text_center_x, text_center_y, text_area)
            
            if (left_line_x < text_center_x < right_line_x) and text_area > self.area_threshold:
                # print("Rack id:", rack_id, "Area:", text_area)
                dist = (abs(text_center_x - self.center_x)**2 + abs(text_center_y - self.center_y)**2)**0.5

                if text_center_x < self.center_x:
                    left_rack_ids.append((rack_id, text_center_y, dist))
                else:
                    right_rack_ids.append((rack_id, text_center_y, dist))

        for rack_id, text_center_y, dist in left_rack_ids:
            if text_center_y < self.center_y:
                Q2_rack_ids.append((rack_id, text_center_y, dist))
            else:
                Q3_rack_ids.append((rack_id, text_center_y, dist))

        for rack_id, text_center_y, dist in right_rack_ids:
            if text_center_y < self.center_y:
                Q1_rack_ids.append((rack_id, text_center_y, dist))
            else:
                Q4_rack_ids.append((rack_id, text_center_y, dist))

        # Q1_rack_id = (min(Q1_rack_ids, key=lambda x:x[1])[0], 'Q1') if Q1_rack_ids else None
        # Q2_rack_id = (min(Q2_rack_ids, key=lambda x:x[1])[0], 'Q2') if Q2_rack_ids else None
        # Q3_rack_id = (max(Q3_rack_ids, key=lambda x:x[1])[0], 'Q3') if Q3_rack_ids else None
        # Q4_rack_id = (max(Q4_rack_ids, key=lambda x:x[1])[0], 'Q4') if Q4_rack_ids else None
        # Q1 & Q2
        if Q1_rack_ids:
            q1_best = min(Q1_rack_ids, key=lambda x: x[2])
            # Q1_rack_id = (q1_best[0], 'Q1')
            rack_dict['Q1'] = q1_best[0]
            Q1_min_value = q1_best[1]
        else:
            Q1_rack_id = None
            Q1_min_value = None

        if Q2_rack_ids:
            q2_best = min(Q2_rack_ids, key=lambda x: x[2])
            # Q2_rack_id = (q2_best[0], 'Q2')
            rack_dict['Q2'] = q2_best[0]
            Q2_min_value = q2_best[1]
        else:
            Q2_rack_id = None
            Q2_min_value = None

        # Overall min between Q1 and Q2
        self.overall_min_y = min(
            v for v in [Q1_min_value, Q2_min_value] if v is not None
        ) if Q1_min_value is not None or Q2_min_value is not None else None


        # Q3 & Q4
        if Q3_rack_ids:
            q3_best = min(Q3_rack_ids, key=lambda x: x[2])
            # Q3_rack_id = (q3_best[0], 'Q3')
            rack_dict['Q3'] = q3_best[0]
            Q3_max_value = q3_best[1]
        else:
            Q3_rack_id = None
            Q3_max_value = None

        if Q4_rack_ids:
            q4_best = min(Q4_rack_ids, key=lambda x: x[2])
            # Q4_rack_id = (q4_best[0], 'Q4')
            rack_dict['Q4'] = q4_best[0]
            Q4_max_value = q4_best[1]
        else:
            Q4_rack_id = None
            Q4_max_value = None

        # Overall max between Q3 and Q4
        self.overall_max_y = max(
            v for v in [Q3_max_value, Q4_max_value] if v is not None
        ) if Q3_max_value is not None or Q4_max_value is not None else None


        # if Q1_rack_id:
        #     all_rack_ids.append(Q1_rack_id) 
        # if Q2_rack_id:
        #     all_rack_ids.append(Q2_rack_id) 
        # if Q3_rack_id:
        #     all_rack_ids.append(Q3_rack_id) 
        # if Q4_rack_id:
        #     all_rack_ids.append(Q4_rack_id) 

        # print(all_rack_ids)
            
        return rack_dict

            
    def compute_bbox(self, vertices):
        area = 0
        center_sum_x = 0
        center_sum_y = 0
        count = 0

        for vertice in vertices:
            xs = [v.x for v in vertice]
            ys = [v.y for v in vertice]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max_x - min_x
            height = max_y - min_y
            center = ((min_x + max_x) / 2, (min_y + max_y) / 2)

            area += width * height
            center_sum_x += center[0]
            center_sum_y += center[1]
            count += 1

        avg_center = (center_sum_x // count, center_sum_y // count) if count else (0, 0)
        return avg_center, area