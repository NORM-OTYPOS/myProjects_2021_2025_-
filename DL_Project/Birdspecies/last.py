import streamlit as st
import tensorflow as tf2
import numpy as np
from PIL import Image
import tensorflow as tf2
import tensorflow.compat.v2 as tf2
import keras


st.set_option('deprecation.showfileUploaderEncoding', False)

@st.cache(allow_output_mutation=True)
def load_model():
	model = tf2.keras.models.load_model("./model1/1")
	return model


def predict_class(image, model):

	image = tf2.cast(image, tf2.float32)
	image = tf2.image.resize(image, [224, 224])

	image = np.expand_dims(image, axis = 0)

	prediction = model.predict(image)

	return prediction


model = load_model()
st.title('Classifier')

file = st.file_uploader("Upload an image of a bird", type=["jpg", "png"])


if file is None:
	st.text('Waiting for upload....')

else:
	slot = st.empty()
	slot.text('Running inference....')

	test_image = Image.open(file)

	st.image(test_image, caption="Input Image", width = 400)

	pred = predict_class(np.asarray(test_image), model)

	class_names = ['ABBOTTS BABBLER', 'ABBOTTS BOOBY', 'ABYSSINIAN GROUND HORNBILL','AFRICAN CROWNED CRANE','AFRICAN EMERALD CUCKOO','AFRICAN FIREFINCH','AFRICAN OYSTER CATCHER','AFRICAN PIED HORNBILL','ALBATROSS','ALBERTS TOWHEE','ALEXANDRINE PARAKEET','ALPINE CHOUGH','ALTAMIRA YELLOWTHROAT','AMERICAN AVOCET','AMERICAN BITTERN','AMERICAN COOT','AMERICAN FLAMINGO','AMERICAN GOLDFINCH','AMERICAN KESTREL','AMERICAN PIPIT']
	#formatted = f"{class_names:,d}"

	result = class_names[np.argmax(pred)]

	output = 'The image is a ' + result

	slot.text('Done')

	st.success(output)