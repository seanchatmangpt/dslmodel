import tempfile
import os
from dslmodel import DataReader, DataWriter

def test_data_read_write():
    # Prepare a sample CSV file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as f:
        f.write('col1,col2\n1,2\n3,4\n')
        file_path = f.name
    # Read data
    data_reader = DataReader(file_path=file_path)
    data = data_reader.forward()
    assert data is not None
    # Write data
    output_path = file_path + '_out.csv'
    data_writer = DataWriter(data=data, file_path=output_path)
    data_writer.forward()
    assert os.path.exists(output_path)
    # Cleanup
    os.remove(file_path)
    os.remove(output_path) 