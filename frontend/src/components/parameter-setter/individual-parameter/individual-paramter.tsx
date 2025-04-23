import { useEffect, useState } from "react";
import useParameters, { StateParameters } from "../../../state/use-parameters";

export const IndividualParameter = (props: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameter: any;
  entry: string;
}) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [value, setValue] = useState<any>(props.parameter.initialValue);
  const [errors, setErrors] = useState<string[]>([]);

  const parameters = useParameters(
    (state: StateParameters) => state.parameters
  );
  const set = useParameters((state: StateParameters) => state.set);

  const getName = () => `${props.entry}-${props.parameter.name}`;

  useEffect(() => {
    const newErrors = [];

    if (props.parameter.constraints.required != undefined && !value)
      newErrors.push(`${props.parameter.name} is required.`);

    if (
      props.parameter.constraints.maxLength != undefined &&
      value?.length > props.parameter.constraints.maxLength
    )
      newErrors.push(
        `${props.parameter.name} should be at most ${props.parameter.constraints.maxLength} characters long.`
      );

    if (
      props.parameter.constraints.max != undefined &&
      value > props.parameter.constraints.max
    )
      newErrors.push(
        `${props.parameter.name} should be at most ${props.parameter.constraints.max}.`
      );

    if (
      props.parameter.constraints.min != undefined &&
      value < props.parameter.constraints.min
    )
      newErrors.push(
        `${props.parameter.name} should be at least ${props.parameter.constraints.min}.`
      );

    setErrors(newErrors);
  }, [value, props]);

  useEffect(() => {
    if (errors.length > 0) return;
    if (parameters.get(getName()) == value) return;

    set(getName(), value);
  }, [errors]);

  return (
    <div className="flex flex-col w-full">
      <label className="text-xs font-bold">{props.parameter.name}</label>
      <input
        className="w-full"
        onChange={(e) => {
          setValue(e.target.value);
        }}
        max={props.parameter.constraints.max ?? undefined}
        min={props.parameter.constraints.min ?? undefined}
        type={props.parameter.type}
      ></input>

      <div className="text-xs font-bold text-red-500">
        {errors.map((e, i) => (
          <p key={i}>{e}</p>
        ))}
      </div>
    </div>
  );
};
