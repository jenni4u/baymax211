import math

class ColorDetectionAlgorithm:

    #---------- CONSTRUCTOR ----------#
    
    """
    Constructor that creates the dictionary of color cluster centers
    """
    def __init__(self):
        self.clusters = self.create_dictionary_of_clusters()


    #--- DICTIONARY OF CLUSTER CENTERS  ---#

    """
    Function that read through all the measurements taken of a specific color and determine the mean normalized RGB values

    Args:
        filename (String): The file that contains the list of measurements of a specific color

    Returns:
        float: The mean normalized RGB values for a specific color
    """
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

                # Get the RGB values from the line that represents one measurement and split them into 3 variables
                rgb_values = line.split(",")
                red_value = float(rgb_values[0].split('=')[1])
                green_value = float(rgb_values[1].split('=')[1])
                blue_value = float(rgb_values[2].split('=')[1])


                # Calculate the total of these values used to find the normalized RGB values
                total = red_value + green_value + blue_value

                # This means the RGB values are all equal to 0, so bad measurement. Skip it
                if total == 0:
                    continue  

                # Find the normalized RGB values by dividing the RGB value by the total and add it to the sum of RGB normalized values
            
                red_normalized_total += red_value / total
                green_normalized_total += green_value / total
                blue_normalized_total += blue_value / total
                
                    
        
                counter_lines +=1

        # Divide the total RGB normalized value by the number of measurements to get a mean
        mean_red = red_normalized_total / counter_lines
        mean_green = green_normalized_total / counter_lines
        mean_blue = blue_normalized_total / counter_lines

        return mean_red, mean_green, mean_blue # return the center of the cluster


    """
    Function that creates a dictionary containing the cluster centers of multiple colors (stickers, room, door)
    The key is the color name and the value is the cluster center

    Returns:
        dictionary: The dictionary of cluster centers
    """
    def create_dictionary_of_clusters(self) :
        clusters = {}

        # Each file of measurements is located at Color files/ color
        for color in ["blue", "green", "purple", "red", "orange", "yellow"]:
            clusters[color] = self.find_cluster_of_colored_block(f"/home/pi/ecse211/baymax211/Color files/{color}.csv")
        return clusters
    
    
    #----------- CLASSIFICATION OF THE COLOR ----------- #
    """
    Function that calculates the distance between 2 systems of 3 variables

    Returns:
        int: The distance calculated
    """
    def calculate_distance(self, x1, y1, z1, x2, y2, z2) :
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
        return distance 



    """
    Function that takes the RGB values of an unknown color, normalize them and calculate the distance between these unknown normalized RGB values
    and the RGB values of each sampled color contained in the dictionary of cluster centers

    Args:
        unknown_red (int): The Red value of the unknown color
        unknown_green (int): The Green value of the unknown color
        unknown_blue (int): The Blue value of the unknown color

    Returns:
        String: The dictionary color that has the closest distance to the unknown color
    """
    
    def classify_the_color(self, unknown_red, unknown_green, unknown_blue) :  
        total_unknown =   int(unknown_red) + int(unknown_green) + int(unknown_blue)
        
        if total_unknown == 0:
            return "The measurement of the unknown colored block was not correctly taken" 

        # Normalize the RGB values of the unknown color
        
        unknown_red_normalized = unknown_red / total_unknown
        unknown_green_normalized = unknown_green / total_unknown
        unknown_blue_normalized = unknown_blue / total_unknown
        
            

        # Create a dictionary that stores the color names and their distances with the unknown color
        distances = {} 

        clusters = self.clusters

        for color, cluster_values in clusters.items(): # this is how we iterate over a dictionary : https://stackoverflow.com/questions/69205854/iterating-over-dictionary-in-python-and-using-each-value
            red, green, blue = cluster_values
            # Calculate the distance between the unknwon RGB values and the cluster center RGB values
            distance = self.calculate_distance(unknown_red_normalized, unknown_green_normalized, unknown_blue_normalized, red, green, blue)
            # Store this distance in the dictionary of distances, the key being the color name to which the unknown RGB values have been compared to
            distances[color] = distance
         
        # Store the color that has the minimum distance with the unknown color and return it
        closest_color = min(distances, key=distances.get) # get the color with the minimum distance : https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary
        
        return closest_color
    

        

