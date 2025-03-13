import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import cv2

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
EXPLICIT_BATCH = 1 << (int)(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)

def build_engine(model_file):
    with trt.Builder(TRT_LOGGER) as builder, builder.create_network(EXPLICIT_BATCH) as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
        builder.max_workspace_size = 1 << 30  # 1GB
        builder.max_batch_size = 1
        with open(model_file, 'rb') as model:
            if not parser.parse(model.read()):
                print('Failed to parse the ONNX model.')
                return None
        return builder.build_cuda_engine(network)

def load_images_to_buffer(pics, pagelocked_buffer):
    preprocessed = np.asarray(pics).ravel()
    np.copyto(pagelocked_buffer, preprocessed)

def main():
    engine = build_engine("yolov3.onnx")
    with engine.create_execution_context() as context:
        host_inputs  = np.zeros(engine.get_binding_shape(0), dtype=np.float32)
        cuda_inputs  = cuda.mem_alloc(host_inputs.nbytes)
        host_outputs = np.zeros(engine.get_binding_shape(1), dtype=np.float32)
        cuda_outputs = cuda.mem_alloc(host_outputs.nbytes)
        stream = cuda.Stream()

        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Preprocess the frame to fit the model input
            input_image = cv2.resize(frame, (416, 416))  # Assuming the model expects 416x416 input
            input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
            input_image = (input_image / 255.0).astype(np.float32)
            
            load_images_to_buffer(input_image, host_inputs)

            # Transfer input data to the GPU.
            cuda.memcpy_htod_async(cuda_inputs, host_inputs, stream)
            
            # Execute the model.
            context.execute_async(batch_size=1, bindings=[int(cuda_inputs), int(cuda_outputs)], stream_handle=stream.handle)
            
            # Transfer predictions back from the GPU.
            cuda.memcpy_dtoh_async(host_outputs, cuda_outputs, stream)
            stream.synchronize()

            # Post-processing: extract bounding boxes and calculate the largest
            output = host_outputs.reshape(-1, 85)  # Assuming each row corresponds to detection
            boxes = []
            for detection in output:
                x, y, w, h, conf, *classes = detection
                if conf > 0.5:  # Threshold confidence
                    class_id = np.argmax(classes)
                    if class_id == 0:  # Assuming 'person' class_id is 0
                        x_center = x - w / 2
                        y_center = y - h / 2
                        boxes.append((x_center, y_center, w, h, conf))

            if boxes:
                largest_box = max(boxes, key=lambda b: b[2] * b[3])  # Select box with largest area
                x_center, y_center, w, h, conf = largest_box
                center_of_webcam = (frame.shape[1] // 2, frame.shape[0] // 2)
                distance_x = center_of_webcam[0] - (x_center + w / 2)
                distance_y = center_of_webcam[1] - (y_center + h / 2)
                
                print(f"Distance from Center: X={distance_x}, Y={distance_y}")

            # Show the image
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
