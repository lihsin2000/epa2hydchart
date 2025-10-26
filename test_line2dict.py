import utils
import traceback

def test_line2dict():
    """
    Test the line2dict function with various inputs to ensure it works correctly.
    """
    try:
        # Test case 1: Basic line with spaces
        lines1 = ["  ID1  123  456  \n"]
        result1 = utils.parse_line_to_dictionary(lines=lines1, l=0, position=2)
        print("Test case 1 result:", result1)
        assert result1 == ['', 'ID1', '123', '456', ''], "Test case 1 failed"
        
        # Test case 2: Line with dash not at beginning of item
        lines2 = ["  ID2  123-456  789  \n"]
        result2 = utils.parse_line_to_dictionary(lines=lines2, l=0, position=2)
        print("Test case 2 result:", result2)
        assert result2 == ['', 'ID2', '123', '-456', '789', ''], "Test case 2 failed"
        
        # Test case 3: Line with dash at beginning of item
        lines3 = ["  ID3  -123  456  \n"]
        result3 = utils.parse_line_to_dictionary(lines=lines3, l=0, position=2)
        print("Test case 3 result:", result3)
        assert result3 == ['', 'ID3', '-123', '456', ''], "Test case 3 failed"
        
        print("All tests passed!")
        return True
    except Exception as e:
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_line2dict()
