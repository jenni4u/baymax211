import math

class ColorDetectionAlgorithm:
    
    def __init__(self):
        self.clusters = self.create_dictionary_of_clusters()

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


    def create_dictionary_of_clusters(self) :
        clusters = {}
        for color in ["blue", "green", "purple", "red", "orange", "yellow"]:
            clusters[color] = self.find_cluster_of_colored_block(f"/home/pi/ecse211/baymax211/Color files/{color}.csv")
        return clusters
    
    
    def classify_the_color(self, unknown_red, unknown_green, unknown_blue) :  
        total_unknown =   int(unknown_red) + int(unknown_green) + int(unknown_blue)
        
        if total_unknown == 0:
            return "The measurement of the unknown colored block was not correctly taken" 

        unknown_red_normalized = unknown_red / total_unknown
        unknown_green_normalized = unknown_green / total_unknown
        unknown_blue_normalized = unknown_blue / total_unknown

        distances = {} # create a dictionary that stores the color names and their distances with the unknown color
        clusters = self.clusters

        for color, cluster_values in clusters.items(): # this is how we iterate over a dictionary : https://stackoverflow.com/questions/69205854/iterating-over-dictionary-in-python-and-using-each-value
            red, green, blue = cluster_values
            distance = self.calculate_distance(unknown_red_normalized, unknown_green_normalized, unknown_blue_normalized, red, green, blue)
            distances[color] = distance
         

        closest_color = min(distances, key=distances.get) # get the color with the minimum distance : https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary
                    

        
        return closest_color
    

        

