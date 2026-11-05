import { selectableWeeks, weekLabel } from '../../lib/weeks';

interface WeekPickerProps {
  value: string;
  onChange: (week: string) => void;
}

export function WeekPicker({ value, onChange }: WeekPickerProps) {
  return (
    <div className='flex flex-col gap-1'>
      <label htmlFor='week-select' className='text-xs font-medium text-slate-600'>
        Week
      </label>
      <select
        id='week-select'
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className='rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm'
      >
        {selectableWeeks().map((week) => (
          <option key={week} value={week}>
            {weekLabel(week)}
          </option>
        ))}
      </select>
    </div>
  );
}
