import { View, Text, Pressable, Image, Linking } from "react-native";
import type { TopItem } from "../lib/parse";
import { faviconUrl } from "../lib/parse";
import { generateArticleId } from "../lib/utils";
import VoteButton from "./VoteButton";
import CommentsButton from "./CommentsButton";

type Props = {
  items: TopItem[];
  weekLabel?: string;
};

const rankingStyles = [
  { bg: "bg-indigo-50", border: "border-indigo-100", numBg: "bg-indigo-600", numText: "text-white" },
  { bg: "bg-indigo-50/70", border: "border-indigo-100", numBg: "bg-indigo-500", numText: "text-white" },
  { bg: "bg-indigo-50/50", border: "border-indigo-100", numBg: "bg-indigo-400", numText: "text-white" },
];

export default function Top3({ items, weekLabel }: Props) {
  if (!items || items.length === 0) return null;

  return (
    <View className="bg-white rounded-3xl shadow-sm border border-neutral-100 p-5">
      <View className="flex-row items-center gap-2 mb-4">
        <Text className="text-2xl">🏆</Text>
        <Text className="text-xl font-bold text-neutral-900">
          Top 3 de la semaine
        </Text>
      </View>
      <View className="gap-3">
        {items.slice(0, 3).map((item, idx) => {
          const articleId = generateArticleId(item.url, item.title);
          const style = rankingStyles[idx];

          return (
            <View
              key={item.url}
              className={`${style.bg} ${style.border} border rounded-2xl overflow-hidden`}
            >
              <Pressable
                onPress={() => Linking.openURL(item.url)}
                className="p-4 active:opacity-80"
              >
                <View className="flex-row items-start gap-3">
                  {/* Rank number */}
                  <View className={`${style.numBg} w-8 h-8 rounded-lg items-center justify-center`}>
                    <Text className={`text-base font-bold ${style.numText}`}>{idx + 1}</Text>
                  </View>

                  {/* Content */}
                  <View className="flex-1">
                    <View className="flex-row items-center gap-2 mb-1">
                      <Image
                        source={{ uri: faviconUrl(item.url, 32) }}
                        className="w-4 h-4 rounded"
                        resizeMode="contain"
                      />
                      {item.source && (
                        <Text className="text-xs font-medium text-indigo-600 uppercase tracking-wide">
                          {item.source}
                        </Text>
                      )}
                    </View>
                    <Text className="text-base font-semibold text-neutral-900 leading-6" numberOfLines={2}>
                      {item.title}
                    </Text>
                  </View>
                </View>
              </Pressable>

              {weekLabel && (
                <View className="flex-row items-center justify-between px-4 pb-4 pt-1">
                  <VoteButton
                    articleId={articleId}
                    articleUrl={item.url}
                    weekLabel={weekLabel}
                    source={item.source}
                    category="top3"
                  />
                  <CommentsButton
                    articleId={articleId}
                    articleUrl={item.url}
                    articleTitle={item.title}
                    weekLabel={weekLabel}
                    category="top3"
                    source={item.source || ''}
                  />
                </View>
              )}
            </View>
          );
        })}
      </View>
    </View>
  );
}
