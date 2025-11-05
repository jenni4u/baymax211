import math
import csv 

class ColorDetectionAlgorithm:
    
    def __init__(self):
        self.clusters = self.create_dictionary_of_clusters()
        self.thresholds = self.create_dictionary_of_thresholds()

    def find_cluster_of_colored_block(self, filename) :
        red_normalized_total = 0.0
        green_normalized_total = 0.0
        blue_normalized_total = 0.0
        counter_lines = 0

        with open(filename) as f:
            next(f) # Skip first line (header)
            
            for line in f:

                line = line.strip() # Remove spaces
                if not line:  # Skip empty line
                    continue

                rgb_values = line.split(",")
                red_value = float(rgb_values[0].split('=')[1])
                green_value = float(rgb_values[1].split('=')[1])
                blue_value = float(rgb_values[2].split('=')[1])

                total = red_value + green_value + blue_value

                if total == 0:
                    continue  # This means the RGB values are all equal to 0, so bad measurement. Skip it

                red_normalized_total += red_value / total
                green_normalized_total += green_value / total
                blue_normalized_total += blue_value / total
        
                counter_lines +=1

        mean_red = red_normalized_total / counter_lines
        mean_green = green_normalized_total / counter_lines
        mean_blue = blue_normalized_total / counter_lines

        return mean_red, mean_green, mean_blue # return the center of the cluster


    def calculate_distance(self, x1, y1, z1, x2, y2, z2) :
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
        return distance 

    def compute_threshold_of_colored_block(self, filename) :
        mean_red, mean_green, mean_blue = self.find_cluster_of_colored_block(filename)
        #max_distance = 0
        distances = []

        with open(filename) as f:
            next(f) # Skip first line (header)
            
            for line in f:

                line = line.strip() # Remove spaces
                if not line:  # Skip empty line
                    continue

                rgb_values = line.split(",")
                red_value = float(rgb_values[0].split('=')[1])
                green_value = float(rgb_values[1].split('=')[1])
                blue_value = float(rgb_values[2].split('=')[1])

                total = red_value + green_value + blue_value

                if total == 0:
                    continue  # This means the RGB values are all equal to 0, so bad measurement. Skip it

                red_normalized = red_value / total
                green_normalized = green_value / total
                blue_normalized = blue_value / total
        
                distance = self.calculate_distance(red_normalized, green_normalized, blue_normalized, mean_red, mean_green, mean_blue)
                #if distance > max_distance:
                    #max_distance = distance

                distances.append(distance)

        average_distance_from_cluster_center = sum(distances) / len(distances)
        
        squared_differences = 0
        for d in distances:
            squared_differences += (d - average_distance_from_cluster_center) ** 2 
        
        standard_deviation = (squared_differences/ (len(distances) - 1)) ** 0.5 
        lower_threshold = average_distance_from_cluster_center - 2*standard_deviation
        upper_threshold = average_distance_from_cluster_center + 2*standard_deviation

        #https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        return lower_threshold, upper_threshold


    def create_dictionary_of_clusters(self) :
        clusters = {}
        for color in ["blue", "green", "purple", "red", "orange", "yellow"]:
            clusters[color] = self.find_cluster_of_colored_block(f"/home/pi/ecse211/baymax211/Color_files/{color}.csv")
        return clusters
    
    def create_dictionary_of_thresholds(self) :
        thresholds = {}
        for color in ["blue", "green", "purple", "red","orange", "yellow"]:
            thresholds[color] = self.compute_threshold_of_colored_block(f"/home/pi/ecse211/baymax211/Color_files/{color}.csv")
        return thresholds

    
    def classify_the_color(self, unknown_red, unknown_green, unknown_blue) :  
        total_unknown =   int(unknown_red) + int(unknown_green) + int(unknown_blue)
        
        if total_unknown == 0:
            return "The measurement of the unknown colored block was not correctly taken" 

        unknown_red_normalized = unknown_red / total_unknown
        unknown_green_normalized = unknown_green / total_unknown
        unknown_blue_normalized = unknown_blue / total_unknown



        distances = {} # create a dictionary that stores the color names and their distances with the unknown color
        clusters = self.clusters
        thresholds = self.thresholds

        for color, cluster_values in clusters.items(): # this is how we iterate over a dictionary : https://stackoverflow.com/questions/69205854/iterating-over-dictionary-in-python-and-using-each-value
            red, green, blue = cluster_values
            distance = self.calculate_distance(unknown_red_normalized, unknown_green_normalized, unknown_blue_normalized, red, green, blue)
            distances[color] = distance
         

        closest_color = min(distances, key=distances.get) # get the color with the minimum distance : https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary
                    
        lower_threshold, upper_threshold = thresholds[closest_color]

        if distances[closest_color] < lower_threshold or distances[closest_color] > upper_threshold:
            return "The threshold is not respected"
        
        return closest_color
    


