## EDA — categorical distributions
### 1. Observations (Data-level)
- `order_status` lệch mạnh về `delivered`; nhóm này áp đảo tuyệt đối so với các trạng thái còn lại.
- Trong các trạng thái không hoàn tất, `cancelled` cao hơn `returned`; `shipped`, `paid`, `created` rất nhỏ. Điều này cho thấy phần lớn order either đi tới hoàn tất hoặc rơi sớm khỏi funnel.
- `payment_method` tập trung mạnh vào `credit_card`; `paypal` và `cod` ở nhóm thứ hai và khá sát nhau; `apple_pay` thấp hơn rõ rệt; `bank_transfer` là nhỏ nhất.
- `order_source` tập trung ở `organic_search`, sau đó là `paid_search` và `social_media`. `email_campaign`, `referral`, `direct` nhỏ hơn đáng kể.
- Có imbalance rõ ở cả 3 biểu đồ: status tập trung vào `delivered`, payment tập trung vào `credit_card`, source tập trung vào search/social.
- Điểm cần lưu ý: `cancelled` lớn hơn `returned`, nên tổn thất có vẻ xảy ra nhiều hơn ở giai đoạn trước giao hàng hơn là sau giao hàng.

### 2. Metric Interpretation
- `delivery_rate`: cao. Tỷ trọng `delivered` vượt xa phần còn lại, phản ánh hệ thống vẫn convert đơn đến completed state khá tốt.
- `return_rate`: thấp đến trung bình-thấp. `returned` có hiện diện nhưng nhỏ hơn nhiều so với `delivered`.
- `cancelled_rate`: không thấp tuyệt đối; đáng chú ý vì là trạng thái thất thoát lớn nhất sau `delivered`.
- Health hệ thống: nhìn chung khỏe ở đầu ra cuối funnel, nhưng vẫn có rò rỉ đáng kể ở bước hoàn tất đơn trước khi giao thành công.

### 3. Business Insights
- Về vận hành: năng lực fulfillment có vẻ ổn vì `delivered` chiếm đa số lớn. Tuy nhiên `cancelled` cao hơn `returned` hàm ý bottleneck vận hành có khả năng nằm trước hoặc trong giai đoạn xử lý đơn hơn là chất lượng hậu giao.
- Về hành vi người dùng: khách hàng ưu tiên phương thức thanh toán quen thuộc và ít friction, đặc biệt là `credit_card`. Việc `cod` vẫn lớn cho thấy còn một tệp cần độ tin cậy cao trước khi trả tiền.
- Về acquisition: đơn hàng đang phụ thuộc mạnh vào `organic_search`, `paid_search`, `social_media`. Đây là các kênh chính nuôi funnel; `direct` nhỏ hơn cho thấy brand pull/returning intent chưa phải nguồn volume lớn.
- Liên hệ business goals:
  - `delivery`: đang là điểm mạnh tương đối.
  - `cancel`: là KPI nên ưu tiên vì đây là thất thoát lớn hơn return.
  - `return`: chưa phải red flag ở view tổng quan này, nhưng vẫn cần theo dõi theo source/payment/product.
  - `funnel`: volume đầu vào chủ yếu đến từ search/social, nên bất kỳ friction nào ở checkout/payment sẽ ảnh hưởng lớn toàn hệ thống.

### 4. Funnel Implications
- `source`: funnel phụ thuộc vào search/social, nên nếu conversion hoặc cancellation kém ở các kênh này thì impact sẽ lớn nhất.
- `payment`: cơ cấu payment khá tập trung; nếu `credit_card` có friction thì ảnh hưởng rộng. Ngược lại, tối ưu checkout cho `credit_card` sẽ có leverage cao nhất.
- `order_status`: bottleneck chính hiện lên ở `cancelled`, không phải `returned`. Nghĩa là mất đơn xảy ra trước khi hoàn tất fulfillment hơn là do trải nghiệm sau mua.

### 5. Actionable Recommendations
- High impact:
  - Phân rã `cancelled_rate` theo `payment_method` và `order_source` để xác định cụm thất thoát lớn nhất trong funnel.
  - Audit checkout flow của `credit_card` vì đây là phương thức chi phối volume; bất kỳ lỗi hay friction nhỏ nào cũng kéo KPI toàn hệ thống.
  - Ưu tiên đánh giá chất lượng traffic của `paid_search` và `social_media` qua conversion-to-delivery, không chỉ volume order.
- Medium:
  - So sánh `delivery_rate`, `cancelled_rate`, `return_rate` giữa `organic_search`, `paid_search`, `social_media` để tối ưu budget acquisition theo chất lượng đơn, không chỉ số lượng.
  - Kiểm tra nhóm `cod` riêng vì đây là payment có rủi ro vận hành/cancel thường đáng theo dõi trong e-commerce, dù biểu đồ này chưa đủ để kết luận.
- Low:
  - Theo dõi `bank_transfer` và `apple_pay` như các kênh thanh toán niche; chưa thấy dấu hiệu cần ưu tiên xử lý chỉ từ phân bố volume.
- Kết luận ưu tiên: chưa có dấu hiệu vấn đề lớn ở `delivery` hay `return` tại level tổng quan; vấn đề nổi bật nhất từ biểu đồ này là cần kiểm soát `cancelled` và đánh giá chất lượng funnel theo `source x payment_method`.