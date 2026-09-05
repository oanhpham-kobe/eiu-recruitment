"use client";

import type { EducationItem } from "@/lib/commands/candidate-submission";

interface EducationSectionProps {
  items: EducationItem[];
  onChange: (items: EducationItem[]) => void;
  disabled?: boolean;
}

export function EducationSection({
  items,
  onChange,
  disabled = false,
}: EducationSectionProps) {
  const handleAdd = () => {
    const newItem: EducationItem = {
      institutionName: "",
      degreeName: "",
      major: "",
      startYear: new Date().getFullYear() - 4,
      endYear: new Date().getFullYear(),
      gpa: "",
      sortOrder: items.length,
    };
    onChange([...items, newItem]);
  };

  const handleRemove = (index: number) => {
    const updated = items.filter((_, idx) => idx !== index);
    onChange(updated);
  };

  const handleFieldChange = (
    index: number,
    field: keyof EducationItem,
    value: string | number,
  ) => {
    const updated = [...items];
    updated[index] = {
      ...updated[index],
      [field]: value,
    };
    onChange(updated);
  };

  return (
    <fieldset className="form-fieldset">
      <legend className="form-legend">
        Quá trình học tập / Education History (Không bắt buộc / Optional)
      </legend>

      {items.length === 0 ? (
        <p className="file-spec">
          Chưa có thông tin học tập. Nhấn nút bên dưới nếu bạn muốn bổ sung.
        </p>
      ) : (
        items.map((item, index) => (
          <div
            key={`edu-row-${item.sortOrder}-${item.startYear}-${item.institutionName}`}
            className="education-item"
          >
            <div className="education-header">
              <span className="education-title">Học vấn #{index + 1}</span>
              <button
                type="button"
                className="btn btn-danger"
                style={{ minHeight: "36px", padding: "4px 12px" }}
                onClick={() => handleRemove(index)}
                disabled={disabled}
                aria-label={`Xóa mục học vấn ${index + 1}`}
              >
                Xóa / Remove
              </button>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor={`edu-inst-${index}`}>
                  Trường đào tạo / Institution
                </label>
                <input
                  id={`edu-inst-${index}`}
                  type="text"
                  className="form-input"
                  value={item.institutionName}
                  onChange={(e) =>
                    handleFieldChange(index, "institutionName", e.target.value)
                  }
                  disabled={disabled}
                  placeholder="Đại học Quốc tế Miền Đông"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`edu-degree-${index}`}>
                  Bằng cấp - Học vị / Degree
                </label>
                <input
                  id={`edu-degree-${index}`}
                  type="text"
                  className="form-input"
                  value={item.degreeName}
                  onChange={(e) =>
                    handleFieldChange(index, "degreeName", e.target.value)
                  }
                  disabled={disabled}
                  placeholder="Cử nhân / Kỹ sư / Thạc sĩ"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`edu-major-${index}`}>
                  Chuyên ngành / Major
                </label>
                <input
                  id={`edu-major-${index}`}
                  type="text"
                  className="form-input"
                  value={item.major ?? ""}
                  onChange={(e) =>
                    handleFieldChange(index, "major", e.target.value)
                  }
                  disabled={disabled}
                  placeholder="Công nghệ thông tin"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`edu-gpa-${index}`}>
                  Điểm trung bình / GPA
                </label>
                <input
                  id={`edu-gpa-${index}`}
                  type="text"
                  className="form-input"
                  value={item.gpa ?? ""}
                  onChange={(e) =>
                    handleFieldChange(index, "gpa", e.target.value)
                  }
                  disabled={disabled}
                  placeholder="3.5 / 4.0"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`edu-start-${index}`}>
                  Năm bắt đầu / Start Year
                </label>
                <input
                  id={`edu-start-${index}`}
                  type="number"
                  className="form-input"
                  value={item.startYear || ""}
                  onChange={(e) =>
                    handleFieldChange(
                      index,
                      "startYear",
                      Number.parseInt(e.target.value, 10) || 0,
                    )
                  }
                  disabled={disabled}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`edu-end-${index}`}>
                  Năm tốt nghiệp / End Year
                </label>
                <input
                  id={`edu-end-${index}`}
                  type="number"
                  className="form-input"
                  value={item.endYear || ""}
                  onChange={(e) =>
                    handleFieldChange(
                      index,
                      "endYear",
                      Number.parseInt(e.target.value, 10) || 0,
                    )
                  }
                  disabled={disabled}
                />
              </div>
            </div>
          </div>
        ))
      )}

      <button
        type="button"
        className="btn btn-secondary"
        onClick={handleAdd}
        disabled={disabled}
        style={{ marginTop: "8px" }}
      >
        + Thêm quá trình học tập / Add Education
      </button>
    </fieldset>
  );
}
