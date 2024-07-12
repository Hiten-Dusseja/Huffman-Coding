import heapq
import os
import json

reversecode = {}


class BinaryTree:
    def __init__(self, value, frequ ):
        self.value = value
        self.frequ = frequ
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        if other is None: return False
        return self.frequ < other.frequ
    
    def __eq__(self, other):
        if other is None: return False
        return self.frequ == other.frequ 
    
    
class Huffmancode:
    def __init__(self, path):
        self.path = path
        self.__heap = []
        self.__code = {}


    def __frequency_from_text(self,text):
        freq_dict = {}
        for char in text:
            if char not in freq_dict.keys():
                freq_dict[char] = 0
            else:
                freq_dict[char] += 1
        return freq_dict
    
    def __Build_heap(self, frequency_dict):
        for key in frequency_dict.keys():
            frequency = frequency_dict[key]
            binary_tree_node = BinaryTree(key, frequency)
            heapq.heappush(self.__heap, binary_tree_node) 
    
    def __Build_binary_tree(self):
        while len(self.__heap) > 1:
            binary_tree_node_1 = heapq.heappop(self.__heap)
            binary_tree_node_2 = heapq.heappop(self.__heap)
            sum_of_freq = binary_tree_node_1.frequ + binary_tree_node_2.frequ
            newnode = BinaryTree(None,sum_of_freq)
            newnode.left = binary_tree_node_1
            newnode.right = binary_tree_node_2
            heapq.heappush(self.__heap,newnode)
        return 
    
    def __Build_Tree_Code_Helper(self, root, curr_bit):
        if(root == None):
            return
        if root.value is not None: 
            self.__code[root.value] = curr_bit
            reversecode[curr_bit] = root.value
            return
        self.__Build_Tree_Code_Helper(root.left,curr_bit+'0')
        self.__Build_Tree_Code_Helper(root.right,curr_bit+'1')
        
        
    def __Build_Tree_Code(self):
        root = heapq.heappop(self.__heap)
        self.__Build_Tree_Code_Helper(root,'')
    
    def __Build_Encoded_Text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.__code[char]
        
        return encoded_text
    
    def __Build_Padded_Text(self,encoded_text):
        padding_value =  8 - len(encoded_text)%8
        for i in range(padding_value):
            encoded_text += '0'
        padded_info = "{0:08b}".format(padding_value) 
        padded_text = padded_info + encoded_text
        return padded_text        
    
    def __Build_Bite_Array(self, padded_text):
        array = []
        for i in range(0,len(padded_text),8):
            byte = padded_text[i:i+8]
            array.append(int(byte,2))
        
        return array
    
    def __Write_Reversecode_toFile(self,filename):
        with open(filename,'w') as file:
            json.dump(reversecode, file)
    
         
    def compression(self):
        #calculate frequency of each text and store in frequency dict
        #Minheap 
        #construct binary tree
        #find code
        #encrypt using the code
        print("Compressions started!")
        filename,file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        with open(self.path, "r+") as file , open(output_path,"wb") as output:
            text = file.read()
            text = text.rstrip()
            frequency_dict = self.__frequency_from_text(text)
            build_heap = self.__Build_heap(frequency_dict)
            self.__Build_binary_tree()
            self.__Build_Tree_Code()
            encoded_text = self.__Build_Encoded_Text(text)
            padded_text = self.__Build_Padded_Text(encoded_text)
            bytes_array = self.__Build_Bite_Array(padded_text)
            final_bytes = bytes(bytes_array)
            output.write(final_bytes)
            self.__Write_Reversecode_toFile(filename+".json")
        print("Compressed successfully!!")
        return output_path
    

class decompression:
    def __init__(self):
        self.__reversecode = {}
        
    def __Remove_padding(self, text):
        padded_info = text[:8]
        padding_value = int(padded_info,2)
        text = text[8:]
        text = text[:-1*padding_value]
        return text
    
    def __Read_reversecode_fromfile(self, filename):
        with open(filename, 'r') as file:
            self.__reversecode = json.load(file)
            
    def __Decoded_Text(self, text):
        current_bits = ''
        decoded_text = ''
        for char in text:
            current_bits += char
            if current_bits in self.__reversecode:
                decoded_text += self.__reversecode[current_bits]
                current_bits = ''
        return decoded_text
    
    def decompress(self,input_path):
        filename,file_extension = os.path.splitext(input_path)
        output_path = filename + '_decompressed' + '.txt'
        self.__Read_reversecode_fromfile(filename+".json")
        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ''
            byte = file.read(1)
            while byte:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8,'0')
                bit_string += bits
                byte = file.read(1)
            text_after_removing_padding = self.__Remove_padding(bit_string)     
            actual_text = self.__Decoded_Text(text_after_removing_padding)  
            output.write(actual_text)   
        return output_path
    
path = input("Enter the path of the file: ")
h = Huffmancode(path)
compressed_file = h.compression()
file_to_be_decompressed = input("Enter the path of the file to be decompressed: ")
d = decompression()
d.decompress(file_to_be_decompressed)
