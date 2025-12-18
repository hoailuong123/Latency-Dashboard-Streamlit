import json
import re
import pandas as pd
 
def convert_telemetry_to_csv(input_file, output_file):
    try:
        # 1. Đọc nội dung file
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
 
        # 2. Làm sạch dữ liệu (Data Cleaning)
        # Loại bỏ các thẻ (kể cả khi chúng nằm giữa dòng)
        # Pattern tìm kiếm chuỗi bắt đầu bằng
        # cleaned_content = re.sub(r'\', '', raw_content)
        # Mẫu Regex đúng để tìm và xóa các thẻ
        cleaned_content = re.sub(r'\'', '', raw_content)
       
        # Xóa các khoảng trắng thừa ở đầu/cuối
        cleaned_content = cleaned_content.strip()
 
        # 3. Chuẩn hóa về dạng JSON List hợp lệ
        # Dữ liệu hiện tại là các object rời rạc: {obj1} {obj2} ...
        # Cần chuyển thành: [{obj1}, {obj2}, ...]
       
        # Tìm các vị trí đóng ngoặc nhọn liền kề mở ngoặc nhọn "}{" (có thể có xuống dòng)
        # và thay thế bằng "}, {" để ngăn cách các phần tử
        json_array_str = re.sub(r'\}\s*\{', '}, {', cleaned_content)
       
        # Bao bọc toàn bộ bằng ngoặc vuông []
        json_final_str = f"[{json_array_str}]"
 
        # 4. Parse JSON
        data = json.loads(json_final_str)
 
        # 5. Chuyển đổi sang DataFrame và lưu CSV
        df = pd.DataFrame(data)
        df['run_id'] = 8
       
        cols_order = ['request_id', 'model_name', 'latency_ms','device_model','app_version', 'crash_log',  'user_feedback',
                      'device_temperature',  'battery_percentage', 'run_id']
        # Chỉ sắp xếp nếu các cột này tồn tại trong dữ liệu
        existing_cols = [col for col in cols_order if col in df.columns]
        df = df[existing_cols]
 
        # Lưu file
        df.to_csv(output_file, index=False)
       
        print(f"✅ Đã chuyển đổi thành công! File lưu tại: {output_file}")
        print(f"📊 Tổng số dòng dữ liệu: {len(df)}")
        print("🔍 5 dòng đầu tiên:")
        print(df.head())
 
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi giải mã JSON: {e}")
        # In ra một phần vị trí lỗi để debug
        print(f"Vị trí lỗi trong chuỗi đã clean: {json_final_str[e.pos-20:e.pos+20]}")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
 
# --- Cấu hình đường dẫn ---
input_filename = 'logs+stepladder_Good+gemma3_4B_qat_4bit+74.txt' # Tên file input của bạn
output_filename = 'telemetry_data_Model gemma3_4B_qat_4bit.csv'

# Chạy hàm chuyển đổi
if __name__ == "__main__":
    # Lưu ý: Đảm bảo file .txt nằm cùng thư mục với script này
    convert_telemetry_to_csv(input_filename, output_filename)