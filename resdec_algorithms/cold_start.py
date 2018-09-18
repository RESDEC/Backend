import numpy as np


class ColdStart:
    def __init__(self, file_rating_path=None, delimiter=None, dict_items=None, number_recommendations=None):
        self.file_rating_path = file_rating_path
        self.delimiter = delimiter
        self.dict_items = dict_items
        self.number_recommendations = number_recommendations

    def calculate_cold_start(self):
        print("calculating cold start... Items to Evaluate: " + str(self.dict_items.__len__()))
        print("calculating cold start... File Rating: " + self.file_rating_path)
        print("calculating cold start... Number of recommendations: " + str(self.number_recommendations))

        arr_data_csv = np.genfromtxt(self.file_rating_path, delimiter=self.delimiter, dtype=None)
        # Dictionary with items and values
        dict_items_values = {}
        for key, value in self.dict_items.iteritems():
            # Dictionary of items, to store counter and sum
            dict_items_values[value] = [0, 0.00]

        # Iterating csv file
        for data in arr_data_csv:
            if str(data[0]).strip() in dict_items_values.keys():
                # Storing the counter
                dict_items_values[str(data[0]).strip()][0] += 1
                # Storing the value
                dict_items_values[str(data[0]).strip()][1] += data[2]

        list_result = []
        for key, value in dict_items_values.iteritems():
            if value[0] > 0:
                tuple_result = (key, float(value[1] / value[0]))
                list_result.append(tuple_result)

        # Sort list of tuples
        list_result.sort(key=lambda x: float(x[1]), reverse=True)

        print("\nCold Start >> Recommended items:")
        dict_items_result = {}
        x = 0
        for i in list_result[:int(self.number_recommendations)]:
            x += 1
            dict_items_result[x] = i[0]
            print("- " + i[0])

        return dict_items_result
