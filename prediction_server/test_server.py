from client import ClassificationClient
from data import to_data_set
import time
from parameters import INPUT_SHAPE, INPUT_TYPE
from model import MultiClassifier

to_label = MultiClassifier.CLASSES()

if __name__ == "__main__":
    x,y = to_data_set()
    x = x['val']
    y = y['val']
    client = ClassificationClient()
    client.start()
    for i in range(y.shape[0]):
        batch_sz = 1
        feat = x[i:i+1]
        print(i, to_label[y[i]])
        client.request_prediction(feat.astype(INPUT_TYPE))
        time.sleep(1/30)
