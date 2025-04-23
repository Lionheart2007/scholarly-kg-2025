import { IndividualParameter } from "./individual-parameter/individual-paramter";

export const ParameterSetter = (props: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameters: any[] | undefined;
  entry: string;
}) => {
  return (
    <div className="w-full flex flex-col gap-2">
      <h3 className="font-bold pb-2">Parameters</h3>

      {props.parameters == undefined || props.parameters.length == 0 ? (
        <span className="text-gray-400">No parameters to set</span>
      ) : (
        props.parameters.map((p, i) => (
          <IndividualParameter
            entry={props.entry}
            key={i}
            parameter={p}
          ></IndividualParameter>
        ))
      )}
    </div>
  );
};
