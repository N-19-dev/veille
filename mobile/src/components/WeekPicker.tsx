import { View, Text, Pressable, Modal, ScrollView } from "react-native";
import { useState } from "react";
import type { WeekMeta } from "../lib/parse";

type Props = {
  weeks: WeekMeta[];
  currentWeek: WeekMeta | null;
  onSelect: (week: WeekMeta) => void;
};

export default function WeekPicker({ weeks, currentWeek, onSelect }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (week: WeekMeta) => {
    onSelect(week);
    setIsOpen(false);
  };

  return (
    <>
      {/* Trigger button */}
      <Pressable
        onPress={() => setIsOpen(true)}
        className="bg-neutral-100 px-3 py-2 rounded-lg flex-row items-center gap-2 active:bg-neutral-200"
      >
        <Text className="text-sm font-medium text-neutral-700">
          {currentWeek?.week || "..."}
        </Text>
        <Text className="text-neutral-400 text-xs">▼</Text>
      </Pressable>

      {/* Modal */}
      <Modal
        visible={isOpen}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setIsOpen(false)}
      >
        <View className="flex-1 justify-end bg-black/50">
          <View className="bg-white rounded-t-2xl max-h-[70%]">
            {/* Header */}
            <View className="flex-row items-center justify-between px-4 py-3 border-b border-neutral-200">
              <Text className="text-lg font-bold text-neutral-900">
                Choisir une semaine
              </Text>
              <Pressable
                onPress={() => setIsOpen(false)}
                className="p-2"
              >
                <Text className="text-neutral-500 text-lg">✕</Text>
              </Pressable>
            </View>

            {/* Week list */}
            <ScrollView className="p-2">
              {weeks.map((week) => {
                const isSelected = currentWeek?.week === week.week;
                return (
                  <Pressable
                    key={week.week}
                    onPress={() => handleSelect(week)}
                    className={`flex-row items-center justify-between p-4 rounded-xl mb-1 ${
                      isSelected ? "bg-indigo-600" : "bg-neutral-50 active:bg-neutral-100"
                    }`}
                  >
                    <View>
                      <Text
                        className={`text-base font-semibold ${
                          isSelected ? "text-white" : "text-neutral-900"
                        }`}
                      >
                        {week.week}
                      </Text>
                      {week.range && (
                        <Text
                          className={`text-sm ${
                            isSelected ? "text-slate-300" : "text-neutral-500"
                          }`}
                        >
                          {week.range}
                        </Text>
                      )}
                    </View>
                    {isSelected && (
                      <Text className="text-white text-lg">✓</Text>
                    )}
                  </Pressable>
                );
              })}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </>
  );
}
